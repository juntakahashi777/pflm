// originally written by Bob Dondero, to whom many thanks.

import java.io.*;

public class CAStest {
  public static void prl(String s) { System.out.println(s); }

  public static void main(String[] args) {
    CASClient casClient = new CASClient();
    String netid = casClient.authenticate();

    prl("Content-type: Text/html");
    prl("");
    prl("<p>Hello from the other side, " + netid);
    prl("<p>Think of this as the main page of your application after " +
          netid + " has been authenticated.");
  }
}
