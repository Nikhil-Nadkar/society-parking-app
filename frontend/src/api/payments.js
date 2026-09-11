import client from "./client";

export const getYearDashboard = (year) => client.get(`/api/payments/dashboard/${year}`).then((r) => r.data);

export const getMyPayments = () => client.get("/api/payments/me").then((r) => r.data);

export const submitPayment = ({ month, year, description, screenshot }) => {
  const formData = new FormData();
  formData.append("month", month);
  formData.append("year", year);
  if (description) formData.append("description", description);
  formData.append("screenshot", screenshot);

  return client
    .post("/api/payments", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};

export const getParkingMap = () => client.get("/api/parking/map").then((r) => r.data);
