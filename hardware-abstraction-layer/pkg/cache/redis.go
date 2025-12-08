package cache

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"sync"
	"time"

	"github.com/redis/go-redis/v9"
)

var rds *redis.Client

type Redis struct {
	db       int
	host     string
	mu       sync.Mutex
	prefix   string
	password string
	tls      *tls.Config
}

func NewRedisClient(host string, password string, db int, prefix string, caCert []byte) Cache {
	var tlsConfig *tls.Config
	if len(caCert) > 0 {
		caCertPool := x509.NewCertPool()
		if ok := caCertPool.AppendCertsFromPEM(caCert); ok {
			tlsConfig = &tls.Config{
				RootCAs: caCertPool,
			}
		}
	}
	return &Redis{
		db:       db,
		host:     host,
		mu:       sync.Mutex{},
		prefix:   prefix,
		password: password,
		tls:      tlsConfig,
	}
}

func (r *Redis) getRedisClient() *redis.Client {
	if rds == nil {
		rds = redis.NewClient(&redis.Options{
			Addr:        r.host,
			Password:    r.password,
			DB:          r.db,
			TLSConfig:   r.tls,
			PoolSize:    10,
			PoolTimeout: time.Millisecond * 20,
		})
	}
	return rds
}

func (r *Redis) Get(ctx context.Context, key string) (interface{}, error) {
	rdb := r.getRedisClient()
	return rdb.Get(ctx, fmt.Sprintf("%s:%s", r.prefix, key)).Result()
}

func (r *Redis) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	rdb := r.getRedisClient()
	return rdb.Set(ctx, fmt.Sprintf("%s:%s", r.prefix, key), value, ttl).Err()
}

func (r *Redis) Delete(ctx context.Context, key string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	rdb := r.getRedisClient()
	return rdb.Del(ctx, fmt.Sprintf("%s:%s", r.prefix, key)).Err()
}

func (r *Redis) Ping(ctx context.Context) error {
	rdb := r.getRedisClient()
	return rdb.Ping(ctx).Err()
}
