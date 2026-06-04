import { auth } from "@/auth";
import { redirect } from "next/navigation";
import SigninClient from "./signin-client";

export default async function SigninPage() {
  const session = await auth();
  if (session?.user) {
    redirect("/dashboard");
  }

  return <SigninClient />;
}