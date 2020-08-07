package com.example.studentmagicbox;
import com.example.studentmagicbox.Beans.*;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.res.AssetManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.provider.ContactsContract;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;

public class MainActivity extends AppCompatActivity {
    private final int LOADING=1;
    private String loginname;
    private String password;
    EditText userlogin;
    EditText userpassword;
    Button check;
    private void initPython() {
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
            Python py = Python.getInstance();
            py.getModule("sys").get("path").callAttr("append", getFilesDir().getAbsolutePath());
        }
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        initPython();
        setContentView(R.layout.activity_main);
        userlogin=(EditText)findViewById(R.id.userlogin);
        userpassword=(EditText)findViewById(R.id.userpassword);
        check=findViewById(R.id.check);
        new LoadingThread().start();
        new EmailThread().start();
        new ClassRoomThread().start();
        check.setOnClickListener(evt->
        {
            loginname=userlogin.getText().toString();
            password=userpassword.getText().toString();
            emailHandler.obtainMessage(1,"11").sendToTarget();
            patchHandler.obtainMessage(1,"11").sendToTarget();
            classHandler.sendEmptyMessageDelayed(1,1780);
        });
    }

    private Handler patchHandler,emailHandler,classHandler;

    private void Loding()
    {
        PyObject o=Python.getInstance().getModule("hello").callAttr("getgrade",loginname,password);
        GradeBean data=o.toJava(GradeBean.class);
        Toast.makeText(MainActivity.this,Float.toString(data.GPA),Toast.LENGTH_LONG).show();
    }

    class LoadingThread extends  Thread {
        @SuppressLint("HandlerLeak")
        @Override
        public void run() {
            super.run();
            Looper.prepare();
            patchHandler = new Handler() {
                @Override
                public void handleMessage(@NonNull Message msg) {
                    super.handleMessage(msg);
                    PyObject o = Python.getInstance().getModule("hello").callAttr("getgrade", loginname, password);
                    GradeBean data = o.toJava(GradeBean.class);
                    Toast.makeText(MainActivity.this, Float.toString(data.GPA), Toast.LENGTH_LONG).show();
                }
            };
            Looper.loop();
        }
    }


    class EmailThread extends Thread{
        @Override
        public void run() {
            super.run();
            Looper.prepare();
            emailHandler=new Handler()
            {
                @Override
                public void handleMessage(@NonNull Message msg) {
                    super.handleMessage(msg);
                    PyObject o=Python.getInstance().getModule("hello").callAttr("getMail_and_Information",loginname,password);
                    EmailBean data= o.toJava(EmailBean.class);
                    for (EmailBean.EmailItem x:data.EmailList)
                        System.out.println(x);
                    System.out.println(data.ecard_year);
                }
            };
            Looper.loop();
        }
    }

    class ClassRoomThread extends Thread{
        @Override
        public void run() {
            super.run();
            Looper.prepare();
            classHandler=new Handler(){
                @Override
                public void handleMessage(@NonNull Message msg) {
                    super.handleMessage(msg);
                    PyObject o=Python.getInstance().getModule("hello").callAttr("getClassRoom",loginname,password);
                    ClassroomBean data=o.toJava(ClassroomBean.class);
                    for(int i=0;i<=6;++i)
                    {
                        System.out.println("第"+i+"节："+data.RoomList[i].size());
                    }
                    System.out.println(data.timeinfo);
                }
            };
            Looper.loop();
        }
    }

}