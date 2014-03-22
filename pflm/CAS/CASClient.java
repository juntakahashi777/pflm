//----------------------------------------------------------------------
// PennypackJavaAuthCas/CASClient.java
// Author: Bob Dondero, based upon similar PHP code written by 
// Scott Karlin and Alex Halderman, and similar Python code written by
// by Brian Kernighan
//----------------------------------------------------------------------

import java.net.*;
import java.util.*;
import java.io.*;

import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.util.StringTokenizer;
import java.util.HashMap;
import java.net.URLDecoder;

public class CASClient
{
   private String casUrl;

   public CASClient()
   {
      casUrl = "https://fed.princeton.edu/cas/";
   }

   public CASClient(String casUrl)
   {
      this.casUrl = casUrl;
   }

   // Authenticate the remote user, and return the user's NetID.
   // Upon the first call, redirect the browser to a login page to
   // complete the authentication process.  (The login page then
   // redirects the browser back to the current page.)
   // Upon subsequent calls, confirm that the login was successful
   // and return the NetID.  Do not return unless the user is
   // successfully authenticated.
   public String authenticate()
   {
      // If the request contains a login ticket, try to validate it.
      HashMap<String,String> fields = Cgi.getFormFields();
      String ticket = fields.get("ticket");
      if (ticket != null)
      {  String netid = validate(ticket);
         if (netid != null)
            return netid;
      }

      // No valid ticket; redirect the browser to the login page
      // to get one.
      String loginUrl = casUrl;
      loginUrl += "login?service=";
      try { loginUrl += URLEncoder.encode(serviceURL(), "UTF-8"); }
      catch (Exception e) { System.err.println(e); }

      System.out.println("Location: " + loginUrl);
      System.out.println(
         "Status-line: HTTP/1.1 307 Temporary Redirect");
      System.out.println();
      System.exit(0);
      return null;  // Can't get here.
   }

   // Validate a login ticket by contacting the CAS server. If
   // valid, return the user's NetID; otherwise, return null.
   public String validate(String ticket)
   {
      try
      {  String valUrl = casUrl;
         valUrl += "validate?service=";
         valUrl += URLEncoder.encode(serviceURL(), "UTF-8");
         valUrl += "&ticket=";
         valUrl += URLEncoder.encode(ticket, "UTF-8");

         URL url = new URL(valUrl);
         InputStream is = url.openStream();
         InputStreamReader isr = new InputStreamReader(is);
         BufferedReader br = new BufferedReader(isr);

         // Read two lines.  If the first line contains "yes", then
         // the second should contain the user's NetID.
         String line1 = br.readLine();
         if (line1 == null) { br.close(); return null; }
         if (! line1.contains("yes")) { br.close(); return null; }
         String line2 = br.readLine();
         if (line2 == null) { br.close(); return null; }
         br.close();
         return line2.trim();
      }
      catch (Exception e)
      {  System.err.println(e);
         return null;
      }
   }

   // Return the URL of the current page after stripping out the
   // "ticket" parameter added by the CAS server.
   public String serviceURL()
   {
      String requestUri = System.getenv("REQUEST_URI");
      if (requestUri == null)
         return "something is badly wrong";

      // Build the URL.
      String url = "http://";
      url += System.getenv("HTTP_HOST");
      url += System.getenv("REQUEST_URI");

      // Remove the "ticket" parameter from the URL.
      url = url.replaceAll("ticket=[^&]*&?", "");
      // Remove a trailing question mark and/or ampersand.
      url = url.replaceAll("\\?&?$|&$", "");
      return url;
   }

   // Alternate version of the previous method for those who
   // dislike fancy regular expressions.
   public String serviceURL2()
   {
      String requestUri = System.getenv("REQUEST_URI");
      if ((requestUri == null) || (requestUri.trim().equals("")))
         return "something is badly wrong";

      // Build the URL.
      String url = "http://";
      url += System.getenv("HTTP_HOST");
      url += System.getenv("REQUEST_URI");

      // Remove the "ticket" parameter from the URL.
      String[] siteAndParams = url.split("\\?");
      if (siteAndParams.length < 2)
         return url;
      String newUrl = siteAndParams[0];
      String[] params = siteAndParams[1].split("&");
      String separator = "?";
      for (int i = 0; i < params.length; i++)
         if (! params[i].startsWith("ticket="))
         {  newUrl += separator + params[i];
            separator = "&";
         }
      return newUrl;
   }

   public static void main(String[] args)
   {
      System.err.println("CASClient does not run standalone");
   }
}

//----------------------------------------------------------------------
// PennypackJavaAuthCas/Cgi.java
// Author: Bob Dondero
//----------------------------------------------------------------------

class Cgi
{
   public static final int GET = 0;
   public static final int POST = 1;

   public static int getRequestMethod()
   {
      String requestMethod = System.getenv("REQUEST_METHOD");
      if (requestMethod.toLowerCase().equals("get"))
         return GET;
      return POST;
   }

   public static HashMap<String,String> parseFormFields(String buffer)
   {
      HashMap<String,String> hashMap = new HashMap<String,String>();

      //  Split the buffer into key/value pairs.
      StringTokenizer pairTokenizer =
         new StringTokenizer(buffer, "&");

      while (pairTokenizer.hasMoreTokens())
      {
         String pair = pairTokenizer.nextToken();

         // Split the key/value pair into a key and value.
         StringTokenizer keyValTokenizer =
            new StringTokenizer(pair, "=");

         String key = "";
         if (keyValTokenizer.hasMoreTokens())
            key = keyValTokenizer.nextToken();

         String value = "";
         if (keyValTokenizer.hasMoreTokens())
            value = keyValTokenizer.nextToken();

         try
         {
            key = URLDecoder.decode(key, "UTF-8");
            value = URLDecoder.decode(value, "UTF-8");
         }
         catch (Exception e) { System.err.println(e); }

         hashMap.put(key, value);
      }

      return hashMap;
   }

   public static HashMap<String,String> getFormFields()
   {
      String buffer = "";

      if (getRequestMethod() == GET)
         buffer = System.getenv("QUERY_STRING");
      else  // getRequestMethod() == POST
      {
         InputStreamReader isr = new InputStreamReader(System.in);
         BufferedReader br = new BufferedReader(isr);
         String line;
         try
         {
            while ((line = br.readLine()) != null)
               buffer += line;
         }
         catch (Exception e) { System.err.println(e); }
      }
      return parseFormFields(buffer);
   }

   public static HashMap<String,String> parseCookieFields(String buffer)
   {
      HashMap<String,String> hashMap = new HashMap<String,String>();

      // Parse the buffer into key/value pairs.
      // Will parse incorrectly if a cookie value contains a semicolon.
      // So make sure your application avoids such cookie values.
      // For example, your application could URL-encode cookie values.
      StringTokenizer pairTokenizer = new StringTokenizer(buffer, ";");

      while (pairTokenizer.hasMoreTokens())
      {
         String pair = pairTokenizer.nextToken().trim();

         // Split the key/value pair into a key and value.
         String key = "";
         String value = "";
         int index = pair.indexOf('=');
         if (index == -1)
            key = pair;
         else
         {
            key = pair.substring(0, index);
            value = pair.substring(index+1);
         }
         hashMap.put(key, value);
      }

      return hashMap;
   }

   public static HashMap<String,String> getCookies()
   {
      String buffer = System.getenv("HTTP_COOKIE");
      if (buffer == null)
         return new HashMap<String,String>();

      return parseCookieFields(buffer);
   }
}
