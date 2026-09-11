import client from "./client";

export const registerUser = (payload) => client.post("/api/auth/register", payload).then((r) => r.data);

export const loginUser = (payload) => client.post("/api/auth/login", payload).then((r) => r.data);

export const forgotPassword = (email) => client.post("/api/auth/forgot-password", { email }).then((r) => r.data);

export const resetPassword = (token, new_password) =>
  client.post("/api/auth/reset-password", { token, new_password }).then((r) => r.data);
