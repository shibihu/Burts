package com.example.floatingwidgetdemo // เปลี่ยนเป็นชื่อ package ของคุณ

import android.app.*
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.*
import android.widget.Button
import android.widget.TextView
import androidx.core.app.NotificationCompat

class FloatingService : Service() {

    private lateinit var windowManager: WindowManager
    private var widgetView: View? = null
    private var consoleView: View? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()

        startForegroundServiceNotification()

        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        setupFloatingWidget()
    }

    private fun setupFloatingWidget() {
        // โหลด Layout ของ Widget
        widgetView = LayoutInflater.from(this).inflate(R.layout.layout_floating_widget, null)

        val layoutFlag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val widgetParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutFlag,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 100
            y = 200
        }

        windowManager.addView(widgetView, widgetParams)

        // ระบบ Drag & Drop ให้ลากเคลื่อนย้ายได้
        val rootContainer = widgetView?.findViewById<View>(R.id.root_container)
        rootContainer?.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View?, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        initialX = widgetParams.x
                        initialY = widgetParams.y
                        initialTouchX = event.rawX
                        initialTouchY = event.rawY
                        return true
                    }
                    MotionEvent.ACTION_MOVE -> {
                        widgetParams.x = initialX + (event.rawX - initialTouchX).toInt()
                        widgetParams.y = initialY + (event.rawY - initialTouchY).toInt()
                        windowManager.updateViewLayout(widgetView, widgetParams)
                        return true
                    }
                }
                return false
            }
        })

        // ปุ่ม Play -> สร้าง/แสดง Console Log
        val btnPlay = widgetView?.findViewById<Button>(R.id.btn_play)
        btnPlay?.setOnClickListener {
            showConsoleLog("hello working")
        }

        // ปุ่ม Close Widget -> ปิด Service
        val btnClose = widgetView?.findViewById<Button>(R.id.btn_close_widget)
        btnClose?.setOnClickListener {
            stopSelf()
        }
    }

    private fun showConsoleLog(message: String) {
        // หากมี Console เปิดอยู่แล้ว ให้ลบออกก่อน
        if (consoleView != null) {
            try { windowManager.removeView(consoleView) } catch (_: Exception) {}
        }

        consoleView = LayoutInflater.from(this).inflate(R.layout.layout_console, null)

        val layoutFlag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val consoleParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutFlag,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 100
            y = 450 // ปรากฏอยู่ด้านล่างเมนูหลักเล็กน้อย
        }

        val tvLog = consoleView?.findViewById<TextView>(R.id.tv_console_log)
        tvLog?.text = "[System]: $message\n"

        val btnCloseConsole = consoleView?.findViewById<TextView>(R.id.btn_close_console)
        btnCloseConsole?.setOnClickListener {
            windowManager.removeView(consoleView)
            consoleView = null
        }

        windowManager.addView(consoleView, consoleParams)
    }

    private fun startForegroundServiceNotification() {
        val channelId = "floating_service_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(channelId, "Floating Overlay Service", NotificationManager.IMPORTANCE_LOW)
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("Floating Widget Active")
            .setContentText("Running floating menu in background")
            .setSmallIcon(android.R.drawable.ic_menu_compass)
            .build()

        startForeground(1, notification)
    }

    override fun onDestroy() {
        super.onDestroy()
        if (widgetView != null) windowManager.removeView(widgetView)
        if (consoleView != null) windowManager.removeView(consoleView)
    }
}
