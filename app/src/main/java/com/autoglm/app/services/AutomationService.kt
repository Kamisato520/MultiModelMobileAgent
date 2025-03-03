package com.autoglm.app.service

import android.accessibilityservice.AccessibilityService
import android.graphics.Point
import android.graphics.Bitmap
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.UiDevice
import android.view.accessibility.UiObject
import android.view.accessibility.UiObject2
import android.view.accessibility.UiSelector
import com.autoglm.app.core.By
import com.autoglm.app.core.Template
import com.autoglm.app.utils.ImageMatcher

class AutomationService : AccessibilityService() {
    private lateinit var uiDevice: UiDevice
    private val watchers = mutableListOf<AutomationWatcher>()
    
    override fun onServiceConnected() {
        super.onServiceConnected()
        uiDevice = UiDevice.getInstance(this)
    }

    // 基于uiautomator2的元素定位方式
    fun findElement(selector: UiSelector): UiObject? {
        return try {
            uiDevice.findObject(selector)
        } catch (e: Exception) {
            null
        }
    }

    // 支持多种定位策略
    fun findElementBy(by: By): UiObject2? {
        return try {
            when(by) {
                is By.Text -> uiDevice.findObject(UiSelector().text(by.value))
                is By.Id -> uiDevice.findObject(UiSelector().resourceId(by.value)) 
                is By.Desc -> uiDevice.findObject(UiSelector().description(by.value))
                is By.XPath -> findElementByXPath(by.value)
                else -> null
            }
        } catch (e: Exception) {
            null
        }
    }

    // 基于Airtest的图像识别
    fun findElementByImage(template: Template): Point? {
        return try {
            val screen = takeScreenshot()
            ImageMatcher.findTemplate(screen, template)
        } catch (e: Exception) {
            null
        }
    }
}