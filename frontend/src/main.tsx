// Browser entry point: loads the one stylesheet and mounts the React app.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { useAuthStore } from "./store/authStore";
import "./styles/globals.css";

// Start auth once, outside React, so StrictMode's double rendering cannot subscribe twice.
void useAuthStore.getState().init();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
