## Environment Setup for NLQ Authentication

To set up the authentication system for the NLQ dashboard, you need to configure the following environment variables:

Refer to `example.env` for an example setup.

Authentication Provider:

    AUTH_PROVIDER: This variable defines the authentication strategy that will be used.

        Possible values:

            oauth2-auth-code: Uses the OAuth 2.0 Authorization Code Flow for authentication.

            oauth2-implicit: Uses the OAuth 2.0 Implicit Flow for authentication.

            cookie-redirect: Redirects the user to a separate authentication server on the same domain.

JWT Configuration:

    DECODE_KEY: This is the public key or secret used to decode JWT tokens.

        The value should be set to your actual public key or secret.

    JWT_ALGORITHM: This variable defines the algorithm used to encode the JWT token.

        Possible values:

            HS256, HS384, HS512 (HMAC algorithms)

            RS256, RS384, RS512 (RSA algorithms)

            ES256, ES384, ES512 (ECDSA algorithms)

            PS256, PS384, PS512 (PS algorithms)

    JWT_AUDIENCE: This is the intended recipient of the JWT token, identifying the specific application or service that the token is meant for.

        The value should be set to the appropriate audience for your application, for example nlq-dashboard.

    NLQ_ROLE_FIELD: This variable defines the field in the JWT payload that contains the NLQ role. This role is used to determine the user's access level within the NLQ dashboard.

        The value should be set to the name of the field that holds the NLQ role in the JWT payload, for example nlq_role.

URLs:

    AUTH_LOGIN_URL: This is the URL that the user will be redirected to for authentication.

        This should point to the login page of the integrated platform.

    FRONTEND_URI: This is the URL of the NLQ dashboard, where the user will be redirected after successful authentication.

        This should be set to the base URL of your deployed NLQ dashboard.

OAuth 2.0 Configuration:

    OAUTH_CLIENT_ID: This is the client ID assigned to your NLQ application by the OAuth provider (e.g., Google, Facebook).

        The value should be set to the actual client ID obtained from the OAuth provider.

    OAUTH_CLIENT_SECRET: This is the client secret assigned to your NLQ application by the OAuth provider.

        The value should be set to the actual client secret obtained from the OAuth provider.

    OAUTH_TOKEN_URL: This is the URL that the authentication server will use to exchange the authorization code for an access token (only applicable to oauth2-auth-code).

        The value should be set to the correct token URL provided by the OAuth provider.

Cookie Configuration:

    TOKEN_COOKIE_NAME: This variable defines the name of the cookie that will be used to store the JWT token.

        The value is only applicable when using the cookie-redirect strategy.

CORS Configuration:

    CORS_ORIGINS: This variable defines the list of origins allowed to access the authentication server.

        This is used to enable Cross-Origin Resource Sharing (CORS) for security purposes, allowing the NLQ dashboard to make requests to the authentication server.

        The value should be a comma-separated list of allowed origins.

How to set these environment variables:

You can set these environment variables in several ways:

    Environment File: Create a file named .env in the root directory of your project and define each variable in the format KEY=VALUE.

    Command Line: Use the export command in your terminal to define the environment variables.

    Environment Variables Configuration (e.g., Docker): If you are using Docker, you can set these variables within your Dockerfile or docker-compose.yml file.

## Running the Authentication Server:

Once the environment variables are set, you can run the authentication server. This will start a web server that will handle authentication requests from the NLQ dashboard.

```bash
# Use --reload to watch for changes
# You may change port if required
uvicorn server:app --port=5500
```

## NLQ Authentication Mechanism

To set up the authentication system, first you need to define environment variables. These variables dictate the authentication strategy, the secret key used to decode JWT tokens, the algorithm used to encode the JWT token, and the URLs for authentication and the NLQ dashboard. You also need to configure the specific details of the authentication strategy, like the OAuth client ID and secret if you are using OAuth.

Once the environment variables are defined, you can run the authentication server. The authentication server is a standalone service that manages authentication requests and issues JWT tokens. It is built using FastAPI, a modern, fast, and easy-to-use web framework for Python.

## Architecture

The authentication mechanism uses a microservice approach. This means that the authentication server and the NLQ dashboard are separate services. This architectural choice allows for independent development and deployment of each component.

The authentication server is responsible for managing authentication requests and issuing JWT tokens. The NLQ dashboard receives these JWT tokens and verifies them. The user's role and other data are extracted from the token, allowing the user to access the dashboard's features.
Authentication Strategies

Two authentication strategies are currently implemented:

### Redirect Based:

This strategy redirects the user to the integrated platform for authentication. The user is then redirected back to the NLQ dashboard with a JWT token containing their NLQ role. The JWT token is stored in a secure HTTP cookie on the user's browser, allowing for seamless access to the dashboard. This strategy is ideal when the integrated platform already has a robust authentication system in place.

**NOTE**: This method requires a reverse proxy for usage with the main platform. The following Caddyfile serves as a good starting point

```
:3000 {
	handle /nlq* {
		reverse_proxy localhost:4000
	}

	handle {
		reverse_proxy localhost:8000
	}
}
```

### OAuth Based:

This strategy uses the OAuth 2.0 protocol for authentication and authorization. It supports both implicit and authorization code grant types. In the implicit grant type, the user is redirected to the integrated platform, and the token is received back directly. In the authorization code grant type, the user is redirected to the integrated platform for authorization, then the application retrieves the access token from the integrated platform using an authorization code. Once the access token is received, it's exchanged for a JWT token, which is then used to access the NLQ dashboard. This strategy is useful when integrating with third-party platforms that support OAuth 2.0 authentication.
Server Implementation

The authentication server is built using FastAPI and exposes the following endpoints:

    /auth/verify: This endpoint verifies the JWT token provided in the authorization header or cookie and returns user details if the token is valid.

    /auth/login_stratergy: This endpoint returns information on how to login the user based on the chosen authentication strategy, directing the user to the correct redirect or OAuth URL.

The server dynamically selects the appropriate AuthProvider implementation based on the AUTH_PROVIDER environment variable. This allows for easy switching between authentication strategies without modifying the core server code.
