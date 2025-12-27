using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UIElements;

public class DestroyEvoBG : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void Destroy_Evo_BG()
    {
         GameObject backgroud = GameObject.Find("background");
        Destroy(backgroud);

    }
}
