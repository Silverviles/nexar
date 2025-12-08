package keystore

import (
	"context"
	"fmt"
	"hash/crc32"
	"log/slog"
	"nexar-hal/pkg/cache"

	secretmanager "cloud.google.com/go/secretmanager/apiv1"
	"cloud.google.com/go/secretmanager/apiv1/secretmanagerpb"
)

type google struct {
	projectID string
	cache     cache.Cache
	namespace string
}

func NewGoogleSecretManager(projectID, prefix string, cache cache.Cache) Keystore {
	return &google{
		projectID: projectID,
		cache:     cache,
		namespace: prefix,
	}
}

func (g *google) Get(ctx context.Context, key, version string) (interface{}, error) {
	if version == "" {
		version = "latest"
	}
	key = fmt.Sprintf("projects/%s/secrets/%s/versions/%s", g.projectID, fmt.Sprintf("%s:%s", g.namespace, key), version)
	if g.cache != nil {
		if data, err := g.cache.Get(ctx, key); err == nil {
			return data, nil
		} else {
			slog.DebugContext(ctx, "cache miss", "key", key, "error", err)
		}
	}
	client, err := secretmanager.NewClient(ctx)
	if err != nil {
		slog.ErrorContext(ctx, "Error creating Secret Manager client", "error", err)
		return nil, err
	}
	defer func(client *secretmanager.Client) {
		err := client.Close()
		if err != nil {
			slog.ErrorContext(ctx, "Error closing Secret Manager client", "error", err)
		}
	}(client)
	req := &secretmanagerpb.AccessSecretVersionRequest{
		Name: key,
	}
	resp, err := client.AccessSecretVersion(ctx, req)
	if err != nil {
		slog.ErrorContext(ctx, "Error accessing secret version", "error", err, "key", key)
		return nil, err
	}
	crc32c := crc32.MakeTable(crc32.Castagnoli)
	checksum := int64(crc32.Checksum(resp.Payload.Data, crc32c))
	if checksum != *resp.Payload.DataCrc32C {
		slog.ErrorContext(ctx, "Data corruption detected for secret", "key", key)
		return nil, fmt.Errorf("data corruption detected for secret %s", key)
	}
	if g.cache != nil {
		err = g.cache.Set(ctx, key, resp.Payload.Data, 0)
		if err != nil {
			slog.ErrorContext(ctx, "Error setting cache", "key", key, "error", err)
		}
	}
	return resp.Payload.Data, nil
}

func (g *google) Set(ctx context.Context, key string, value interface{}) error {
	client, err := secretmanager.NewClient(ctx)
	if err != nil {
		slog.ErrorContext(ctx, "Error creating Secret Manager client", "error", err)
		return err
	}
	defer func(client *secretmanager.Client) {
		err := client.Close()
		if err != nil {
			slog.ErrorContext(ctx, "Error closing Secret Manager client", "error", err)
		}
	}(client)
	req := &secretmanagerpb.CreateSecretRequest{
		Parent:   fmt.Sprintf("projects/%s", g.projectID),
		SecretId: fmt.Sprintf("%s:%s", g.namespace, key),
		Secret: &secretmanagerpb.Secret{
			Replication: &secretmanagerpb.Replication{
				Replication: &secretmanagerpb.Replication_Automatic_{
					Automatic: &secretmanagerpb.Replication_Automatic{},
				},
			},
			Labels: map[string]string{
				"namespace": g.namespace,
			},
		},
	}
	secret, err := client.CreateSecret(ctx, req)
	if err != nil {
		slog.ErrorContext(ctx, "Error creating secret", "error", err, "key", key)
		return err
	}
	secretVersionReq := &secretmanagerpb.AddSecretVersionRequest{
		Parent: secret.Name,
		Payload: &secretmanagerpb.SecretPayload{
			Data: value.([]byte),
		},
	}
	_, err = client.AddSecretVersion(ctx, secretVersionReq)
	return err
}

func (g *google) Delete(ctx context.Context, key, version string) error {
	if version != "" {
		version = "latest"
	}
	client, err := secretmanager.NewClient(ctx)
	if err != nil {
		slog.ErrorContext(ctx, "Error creating Secret Manager client", "error", err)
		return err
	}
	defer func(client *secretmanager.Client) {
		err := client.Close()
		if err != nil {
			slog.ErrorContext(ctx, "Error closing Secret Manager client", "error", err)
		}
	}(client)
	secretName := fmt.Sprintf("projects/%s/secrets/%s/versions/%s", g.projectID, fmt.Sprintf("%s:%s", g.namespace, key), version)
	req := &secretmanagerpb.DestroySecretVersionRequest{
		Name: secretName,
	}
	_, err = client.DestroySecretVersion(ctx, req)
	return err
}
