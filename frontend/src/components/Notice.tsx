// A bordered message box for errors and gentle notices. Meaning comes from the words, not color.

import type { ReactNode } from "react";

interface NoticeProps {
  children: ReactNode;
  warning?: boolean;
}

export default function Notice({ children, warning = false }: NoticeProps) {
  return (
    <div className={warning ? "notice notice-warning" : "notice"} role={warning ? "alert" : "status"}>
      {children}
    </div>
  );
}
