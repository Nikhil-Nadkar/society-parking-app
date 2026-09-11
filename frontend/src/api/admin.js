import client, { API_BASE_URL } from "./client";

export const listUsers = () => client.get("/api/admin/users").then((r) => r.data);

export const listParkingSlots = () => client.get("/api/admin/parking").then((r) => r.data);

export const createParkingSlot = (payload) => client.post("/api/admin/parking", payload).then((r) => r.data);

export const assignParkingSlot = (slotId, userId) =>
  client.post(`/api/admin/parking/${slotId}/assign`, { user_id: userId }).then((r) => r.data);

export const listPayments = (statusFilter) =>
  client
    .get("/api/admin/payments", { params: statusFilter ? { status_filter: statusFilter } : {} })
    .then((r) => r.data);

export const approvePayment = (paymentId) =>
  client.post(`/api/admin/payments/${paymentId}/approve`).then((r) => r.data);

export const rejectPayment = (paymentId, rejection_reason) =>
  client.post(`/api/admin/payments/${paymentId}/reject`, { rejection_reason }).then((r) => r.data);

export const screenshotUrl = (paymentId) => `${API_BASE_URL}/api/admin/payments/${paymentId}/screenshot`;
