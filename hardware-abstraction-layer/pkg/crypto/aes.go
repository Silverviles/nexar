package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"fmt"
	"nexar-hal/pkg/keystore"
)

type aesHeader struct {
	KeyVersion string `json:"key_version"`
	Id         string `json:"id"`
	Hash       string `json:"hash"`
}

type aesImpl struct {
	keyVersion string
	keyName    string
	keystore   keystore.Keystore
}

func NewAESImpl(keyVersion, keyName string, keystore keystore.Keystore) Crypto {
	return &aesImpl{
		keyVersion: keyVersion,
		keyName:    keyName,
		keystore:   keystore,
	}
}

func (a *aesImpl) encrypt(data []byte, key []byte) ([]byte, error) {
	cipherBlock, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	gcm, err := cipher.NewGCM(cipherBlock)
	if err != nil {
		return nil, err
	}
	nonce := make([]byte, gcm.NonceSize())
	ciphertext := gcm.Seal(nonce, nonce, data, nil)
	return ciphertext, nil
}

func (a *aesImpl) decrypt(data []byte, key []byte) ([]byte, error) {
	cipherBlock, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	gcm, err := cipher.NewGCM(cipherBlock)
	if err != nil {
		return nil, err
	}
	nonceSize := gcm.NonceSize()
	if len(data) < nonceSize {
		return nil, fmt.Errorf("ciphertext too short")
	}
	nonce, ciphertext := data[:nonceSize], data[nonceSize:]
	return gcm.Open(nil, nonce, ciphertext, nil)
}
