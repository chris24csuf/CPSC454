package com.example.dc2s;

import androidx.appcompat.app.AppCompatActivity;

import android.content.pm.ActivityInfo;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;

public class MainActivity extends AppCompatActivity implements View.OnClickListener{

    protected Button start_button;
    protected TextView status, random, last;
    protected String host, status_msg, random_msg, last_msg;
    protected int port;
    protected OutputStreamWriter sock_out;
    protected InputStream sock_in;
    protected SocketAddress sock_addr;
    protected Socket sock;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        host = "52.53.164.104"; //AWS public IP address of master node
        port = 54321; //some arbitrary port number for project

        start_button = (Button)findViewById(R.id.button_start_id);
        status = (TextView)findViewById(R.id.tv_status_id);
        random = (TextView)findViewById(R.id.tv_random_id);
        last = (TextView)findViewById(R.id.tv_last_id);
        start_button.setOnClickListener(this);
        status.setText("\nDC2S Android Application\nby\nChristian Angeles\nJohn Zavala");
    }

    @Override
    public void onClick(View v) {
        try{
            if(start_button.isPressed()){
                new Socket_ASync().execute();
                status.setText("Starting DC2S simulation...");
                status.setGravity(View.TEXT_ALIGNMENT_CENTER);
                random.setText("");
                last.setText("");
            }
        }
        catch (Exception e){
            System.out.println(e);
        }
    }

    private class Socket_ASync extends AsyncTask<Void, Void, Void>{

        @Override
        protected Void doInBackground(Void... voids) {
            try{
                sock = new Socket();
                sock_addr = new InetSocketAddress(host, port);
                sock.connect(sock_addr, 2000);
                sock_out = new OutputStreamWriter(sock.getOutputStream(), "ASCII");
                sock_in = sock.getInputStream();

                try {

                    sock_out.write("start");
                    sock_out.flush();

                    int read;
                    byte[] buffer = new byte[1024];
                    while((read = sock_in.read(buffer)) != -1) {
                        String msg_recv = new String(buffer, 0, read);
                        String[] str_array = msg_recv.split(" ", 0);
                        status_msg = "Simulation completed with results:";
                        random_msg = "Found the random index in " + str_array[0].trim() + " second(s)";
                        last_msg = "Found the last index in " + str_array[1].trim() + " second(s)";
                    }

                    sock_out.close();
                    sock.close();
                }
                catch (Exception e){
                    System.out.println(e);
                }
            }
            catch (Exception e){
                System.out.println(e);
                status_msg = "Connection error...";
                random_msg = "";
                last_msg = "";
            }
            System.out.println("Socket thread closed");
            return null;
        }

        @Override
        protected void onPostExecute(Void aVoid) {
            status.setText(status_msg);
            random.setText(random_msg);
            last.setText(last_msg);
            super.onPostExecute(aVoid);
        }
    }
}
