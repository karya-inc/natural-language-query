import { useToast } from "@chakra-ui/react";
import { ReactNode, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Login } from "./Login";
import { BACKEND_URL } from "../config";

export type CheckUserAuthProps = {
  forComponent: ReactNode;
};

type LoginResponse =
  | {
    action: "OAUTH2_AUTH_CODE" | "OAUTH2_IMPLICIT" | "REDIRECT_COOKIE";
    /** url to redirect to */
    payload: string;
  }
  | {
    action: "OAUTH2_TOKEN_RESPONSE";
    /** OAuth2 authentication_code reponse with token */
    payload: {
      token_type: "Bearer";
      expires_in: number;
      access_token: string;
      refresh_token: string;
    };
  };
export function CheckUserAuth(props: CheckUserAuthProps) {
  const [isTokenValid, setIsTokenValid] = useState<boolean | null>(null);
  const toast = useToast();
  const [urlSearchParams, setUrlSearchParams] = useSearchParams();

  // Manage access token
  const [accessToken, setAccessToken] = useState<string | null>(
    localStorage.getItem("access_token"),
  );

  useEffect(() => {
    if (accessToken) {
      localStorage.setItem("access_token", accessToken);
    }
  }, [accessToken]);

  /** Show a toast for login error */
  const toastLoginError = (reason?: string) =>
    toast({
      title: "Error",
      description: reason ?? "Failed to login",
      status: "error",
    });

  /** Check if the token is valid
   * TODO: Update function after API is implemented
   */
  const checkToken = async (token?: string | null) => {
    try {
      const headers = new Headers();
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }

      const res = await fetch(`${BACKEND_URL}/auth/verify`, {
        headers,
        method: "GET",
        credentials: "include",
      });

      const data = await res.json();
      if (data?.is_valid) {
        setIsTokenValid(true);
      } else {
        setIsTokenValid(false);
      }
    } catch {
      setIsTokenValid(false);
    }
  };

  /** Login the user
   * TODO: Update function after API is implemented
   */
  const loginUser = async () => {
    try {
      const loginStratergyResponse = await fetch(
        `${BACKEND_URL}/auth/login_stratergy`,
      );
      const loginStratergy: LoginResponse | null =
        await loginStratergyResponse.json();
      if (!loginStratergy) {
        toastLoginError();
        return;
      }

      const action = loginStratergy.action;
      switch (action) {
        case "REDIRECT_COOKIE":
        case "OAUTH2_AUTH_CODE":
        case "OAUTH2_IMPLICIT":
          const url = loginStratergy.payload;
          window.location.replace(url);
          break;

        case "OAUTH2_TOKEN_RESPONSE":
          setAccessToken(loginStratergy.payload.access_token);
          break;
        default:
          console.error(
            "Backend responded with unsupported action for login",
            action,
          );
          break;
      }
    } catch (e: any) {
      toastLoginError(e.toString());
    }
  };

  /** Exchange auth code for token */
  const exchangeCodeForToken = async (code: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/auth/exchange_code`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });
      const token_response: LoginResponse = await res.json();
      if (token_response.action !== "OAUTH2_TOKEN_RESPONSE") {
        toastLoginError("Invalid response from server");
        return;
      }

      setAccessToken(token_response.payload.access_token);
    } catch (e: any) {
      toastLoginError(e.toString());
    }
  };

  useEffect(() => {
    const access_token = urlSearchParams.get("access_token");
    if (access_token) {
      setAccessToken(access_token);
      setUrlSearchParams(urlSearchParams);
      urlSearchParams.delete("access_token");
    }

    const auth_code = urlSearchParams.get("code");
    if (auth_code) {
      exchangeCodeForToken(auth_code);
      urlSearchParams.delete("code");
    }
  }, [urlSearchParams]);

  /** Check if the token is valid */
  useEffect(() => {
    checkToken(accessToken);
  }, [accessToken]);

  if (isTokenValid) {
    console.warn("Token is valid");
    return props.forComponent;
  } else {
    return <Login onLogin={loginUser} />;
  }
}
