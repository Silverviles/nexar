# API Gateway

| | |
|---|---|
| **Directory** | `/api` |
| **Stack** | Express 5, TypeScript, Axios, Winston |
| **Port** | 3000 |

## Overview

The API Gateway is the single entry point for all client requests into the Nexar platform. It sits between the React frontend and the four Python backend services, handling authentication, request proxying, structured logging, and monitoring. No backend service is exposed directly to the internet; all external traffic passes through this gateway.

## Authentication

The gateway implements a full authentication layer built on JWT tokens with Firebase and Firestore as the backing identity store.

- **User Registration and Login** -- Users can create accounts with email and password. Passwords are hashed and stored securely. On successful login, the gateway issues a signed JWT that the client includes in subsequent requests.
- **Email Verification** -- New accounts receive a verification email. Unverified accounts have restricted access until the email address is confirmed.
- **Google OAuth** -- Users can authenticate via Google OAuth as an alternative to email/password registration, streamlining onboarding.
- **Token Management** -- JWTs carry user identity and role claims. The gateway validates tokens on every protected request, rejecting expired or malformed tokens with appropriate HTTP status codes.

## Request Proxying

After authentication, the gateway forwards requests to one of the four Python backend services based on the URL path. Axios is used as the HTTP client for upstream calls. Each proxy route maps a public API path to the corresponding internal service endpoint:

- Code Analysis Engine (port 8002)
- Decision Engine (port 8003)
- AI Code Converter (port 8001)
- Hardware Abstraction Layer (port 8004)

The gateway preserves the original request body and headers, appending internal tracing headers before forwarding.

## Logging and Monitoring

Every inbound request is assigned a **unique request ID** that propagates through all upstream calls, enabling end-to-end tracing across services. Winston provides structured, levelled logging with the following capabilities:

- **Request/Response Logging** -- Method, path, status code, and timing are logged for every request.
- **Upstream Response Time** -- The gateway records how long each backend service takes to respond, surfacing latency in logs.
- **Slow Response Flagging** -- Responses that exceed a configurable threshold are flagged in the logs, making it straightforward to identify performance regressions.

## Protected Routes

All routes that proxy to backend services require a valid JWT. The only public (unauthenticated) endpoints are the authentication routes themselves: registration, login, OAuth callbacks, and email verification. This ensures that no analysis, conversion, or execution request can reach the backend without an authenticated user context.
