import android.media.projection.MediaProjectionManager
import android.graphics.Bitmap
import okhttp3.*
import java.io.ByteArrayOutputStream

private fun captureAndUploadScreen() {
    val mediaProjectionManager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
    val intent = mediaProjectionManager.createScreenCaptureIntent()
    startActivityForResult(intent, REQUEST_CODE)

    // 截屏后的 Bitmap 转换为字节流
    val bitmap: Bitmap = getScreenBitmap()
    val outputStream = ByteArrayOutputStream()
    bitmap.compress(Bitmap.CompressFormat.JPEG, 90, outputStream)
    val byteArray = outputStream.toByteArray()

    // 上传到 OCR 服务
    val requestBody = MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .addFormDataPart("image", "screenshot.jpg", byteArray.toRequestBody())
        .build()

    val request = Request.Builder()
        .url("https://www.myexample.com/api/upload-screenshot")
        .post(requestBody)
        .build()

    client.newCall(request).enqueue(object : Callback {
        override fun onFailure(call: Call, e: IOException) {
            e.printStackTrace()
        }

        override fun onResponse(call: Call, response: Response) {
            // 处理上传结果
        }
    })
}
