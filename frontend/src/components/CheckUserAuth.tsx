import { useToast } from "@chakra-ui/react";
import { ReactNode, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

export type CheckUserAuthProps = {
  forComponent: ReactNode;
};

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
export function CheckUserAuth(props: CheckUserAuthProps) {
  const [isTokenValid, setIsTokenValid] = useState<boolean | null>(null);
  const toast = useToast();
  const [urlSearchParams, setUrlSearchParams] = useSearchParams();

  /** Show a toast for login error */
  const toastLoginError = (reason?: string) =>
    toast({
      id: "login_error",
      title: "Error",
      description: reason ?? "Failed to login",
      status: "error",
    });

  /** Check if the token is valid
   * TODO: Update function after API is implemented
   */
  const checkToken = async (token: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/auth/verify?token=${token}`);
      const data = await res.json();
      if (!data?.is_valid) {
        setIsTokenValid(false);
        return;
      }
    } catch {
      setIsTokenValid(true);
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
      const loginStratergy = await loginStratergyResponse.json();
      if (!loginStratergy) {
        toastLoginError();
        return;
      }

      const action = loginStratergy.action;
      if (action === "redirect") {
        const url = loginStratergy.payload;
        window.location.replace(url);
        return;
      }

      console.error(
        "Backend responded with unsupported action for login",
        action,
      );
    } catch (e: any) {
      toastLoginError(e.toString());
    }
  };

  useEffect(() => {
    if (urlSearchParams.get("auth_token")) {
      localStorage.setItem(
        "token",
        urlSearchParams.get("auth_token") as string,
      );
      urlSearchParams.delete("auth_token");
      setUrlSearchParams(urlSearchParams);
    }
  }, [urlSearchParams]);

  /** Check if the token is valid */
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setIsTokenValid(false);
      return;
    }

    checkToken(token);
  }, []);

  /** Login the user if the token is invalid */
  useEffect(() => {
    if (isTokenValid === false) {
      loginUser();
    }
  }, [isTokenValid]);

  return isTokenValid ? props.forComponent : null;
}
