import axios from "axios"
import {getSession} from "next-auth/react"

const api = axios.create({
    baseURL : "/api/backend",
    headers : {"Content-Type" : "application/json"},
})

api.interceptors.request.use(async(config) => {
     try {
    const session = await getSession();
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`;
    }
  } catch (err) {
    console.error("[api] Failed to get session for request:", err);
  }
  return config;
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn("[api] 401 Unauthorized — token may have expired");
    }
    return Promise.reject(error);
  }
);

export default api;