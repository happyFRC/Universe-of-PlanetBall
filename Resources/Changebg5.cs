using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class NewBehaviourScript2 : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void Background_05()
    {
        GameObject.Find("background").GetComponent<SpriteRenderer>().sprite = Resources.Load<Sprite>("background_05");
    }
}
