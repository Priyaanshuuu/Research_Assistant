import NextAuth from "next-auth"
import type { NextAuthOptions } from "next-auth"

export const authOptions: NextAuthOptions = {
  providers:[

  ],

  session:{

  },

  pages:{

  },

  callbacks:{
    
  }
}

export default NextAuth(authOptions)