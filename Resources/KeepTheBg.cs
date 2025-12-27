using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PersistentBackgroundSaver : MonoBehaviour
{
    public SpriteRenderer targetSpriteRenderer; // 拖入背景的SpriteRenderer
    public string saveKey = "SelectedBackground";
    public Sprite[] availableBackgrounds; // 所有可能的背景图片

    void Start()
    {
        LoadBackground();
    }

    // 设置并保存背景
    public void SetAndSaveBackground(Sprite newBackground)
    {
        if (targetSpriteRenderer != null && newBackground != null)
        {
            targetSpriteRenderer.sprite = newBackground;
            PlayerPrefs.SetString(saveKey, newBackground.name);
            PlayerPrefs.Save();
        }
    }

    // 通过名称设置背景
    public void SetAndSaveBackgroundByName(string backgroundName)
    {
        foreach (Sprite sprite in availableBackgrounds)
        {
            if (sprite.name == backgroundName)
            {
                SetAndSaveBackground(sprite);
                return;
            }
        }
    }

    void LoadBackground()
    {
        if (PlayerPrefs.HasKey(saveKey) && targetSpriteRenderer != null)
        {
            string savedName = PlayerPrefs.GetString(saveKey);
            foreach (Sprite sprite in availableBackgrounds)
            {
                if (sprite.name == savedName)
                {
                    targetSpriteRenderer.sprite = sprite;
                    break;
                }
            }
        }
    }
}