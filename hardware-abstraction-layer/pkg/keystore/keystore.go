package keystore

import "context"

type Keystore interface {
	Get(ctx context.Context, key, version string) (interface{}, error)
	Set(ctx context.Context, key string, value interface{}) error
	Delete(ctx context.Context, key, version string) error
}
