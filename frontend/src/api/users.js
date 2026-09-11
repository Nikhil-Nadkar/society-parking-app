import client from "./client";

export const getMe = () => client.get("/api/users/me").then((r) => r.data);

export const updatePhone = (phone) => client.patch("/api/users/me", { phone }).then((r) => r.data);
