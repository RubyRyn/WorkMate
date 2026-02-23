export interface User {
  id: number;
  email: string;
  name: string;
  picture: string | null;
  role: "admin" | "member";
}
