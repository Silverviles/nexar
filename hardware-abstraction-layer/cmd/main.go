package main

import (
	"context"
	"log/slog"
	"os"
)

func main() {
	_ = context.Background()

	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug}))
	slog.SetDefault(logger)

}
