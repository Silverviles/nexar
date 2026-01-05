import type { CorsOptions } from "cors";

const origins = process.env.FRONT_END_ORIGINS?.split(",") || [
  "http://localhost:3000",
  "http://localhost:5173",
  "http://localhost:8080",
];

export const corsOptions: CorsOptions = {
  origin: origins,
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"],
};
