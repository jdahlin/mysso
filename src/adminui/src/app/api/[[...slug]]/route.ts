import {getAccessToken} from '@auth0/nextjs-auth0';
import {NextResponse} from "next/server";

const forwardURL = async (request: Request) => {
  const {accessToken} = await getAccessToken({});
  const headers = {
    Authorization: `Bearer ${accessToken}`
  };
  const url = new URL(request.url)
  let forwardUrl = url.pathname.slice(4)
  if (url.searchParams.size > 0) {
    forwardUrl += '?' + url.searchParams
  }
  const response = await fetch('https://master.i-1.app' + forwardUrl,
    {headers, method: request.method});
  const data = await response.json();
  return NextResponse.json(data);

}

export async function DELETE(request: Request) { return forwardURL(request) }
export async function GET(request: Request) { return forwardURL(request) }
export async function PUT(request: Request) { return forwardURL(request) }
export async function POST(request: Request) { return forwardURL(request) }
