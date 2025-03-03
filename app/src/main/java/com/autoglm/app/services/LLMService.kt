class LLMService {
    private val client = OkHttpClient()
    private val config = Config()
    
    suspend fun analyzeTextInput(text: String): List<AutomationAction> {
        return withContext(Dispatchers.IO) {
            val request = Request.Builder()
                .url(config.getModelEndpoint("text"))
                .post(createRequestBody(text))
                .build()
                
            val response = client.newCall(request).execute()
            parseResponse(response.body?.string())
        }
    }
    
    suspend fun analyzeScreenshot(bitmap: Bitmap): List<AutomationAction> {
        return withContext(Dispatchers.IO) {
            val base64Image = bitmap.toBase64String()
            val request = Request.Builder()
                .url(config.getModelEndpoint("vision"))
                .post(createMultimodalRequestBody(base64Image))
                .build()
                
            val response = client.newCall(request).execute()
            parseResponse(response.body?.string())
        }
    }
} 