package crypto

import "context"

type Crypto interface {
	Encrypt(ctx context.Context, data interface{}, saltSize int) ([]byte, error)
	Decrypt(ctx context.Context, data []byte) (interface{}, error)
}
