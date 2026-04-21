import type {DefaultSession} from "next-auth"

declare module "next-auth" {
    interface Session {
        accessToken : string
        user:{
            id : string
        } & DefaultSession["User"]
    }

    interface User {
        accessToken?: string
    }
}

declare module "next-auth/jwt" {
    interface JWT {
        userId : string
        accessToken : string
    }
}