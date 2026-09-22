"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api-client";
import { User, AuthResponse } from "@/types/api";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [user, setUser] = useState<User | null>(null);
  const [isLoadingUser, setIsLoadingUser] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem("fitflow_user");
    const token = localStorage.getItem("fitflow_token");

    if (storedUser && token) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem("fitflow_user");
        localStorage.removeItem("fitflow_token");
      }
    }
    setIsLoadingUser(false);
  }, []);

  const loginMutation = useMutation({
    mutationFn: (credentials: { email: string; password: string }) =>
      api.post<AuthResponse>("/auth/login", credentials),
    onSuccess: (data) => {
      localStorage.setItem("fitflow_token", data.access_token);
      localStorage.setItem("fitflow_user", JSON.stringify(data.user));
      setUser(data.user);
      queryClient.clear();
      router.push("/dashboard");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (payload: {
      gym_name: string;
      owner_name: string;
      email: string;
      password: string;
    }) => api.post<AuthResponse>("/auth/register", payload),
    onSuccess: (data) => {
      localStorage.setItem("fitflow_token", data.access_token);
      localStorage.setItem("fitflow_user", JSON.stringify(data.user));
      setUser(data.user);
      queryClient.clear();
      router.push("/dashboard");
    },
  });

  const logout = () => {
    localStorage.removeItem("fitflow_token");
    localStorage.removeItem("fitflow_user");
    setUser(null);
    queryClient.clear();
    router.push("/login");
  };

  return {
    user,
    isLoadingUser,
    isAuthenticated: !!user,
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error as ApiError | null,
    register: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error as ApiError | null,
    logout,
  };
}
