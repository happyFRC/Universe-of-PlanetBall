using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class KEEPTHEBG : MonoBehaviour
{
    
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
     public  void keep()
    {
        GameObject background = GameObject.Find("background");
        DontDestroyOnLoad(background);
        }
    }

