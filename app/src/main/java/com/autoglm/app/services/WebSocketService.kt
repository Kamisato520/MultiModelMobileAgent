class WebSocketService {
    private var webSocket: WebSocket? = null
    private val client = OkHttpClient()
    
    fun connect(deviceId: String) {
        val request = Request.Builder()
            .url("ws://your-server/ws")
            .build()
            
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                handleMessage(text)
            }
        })
    }
    
    private fun handleMessage(message: String) {
        val json = JSONObject(message)
        when (json.getString("type")) {
            "task" -> handleTask(json)
            "status" -> handleStatus(json)
        }
    }
} 