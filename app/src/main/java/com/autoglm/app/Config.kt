class Config {
    companion object {
        const val API_KEY = "sk-4a6e5901c20f43139c2c84d8e9bd50f2"
        
        val MODELS = mapOf(
            "text" to Model("qwen-plus", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"),
            "vision" to Model("qwen-vl-max", "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"),
            "ocr" to Model("qwen-vl-ocr", "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"),
            "audio" to Model("qwen-audio-turbo", "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation")
        )
    }
} 