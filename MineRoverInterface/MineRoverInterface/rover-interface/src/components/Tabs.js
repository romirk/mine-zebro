/* eslint-disable jsx-a11y/no-redundant-roles */
import React from "react";
import "./styles.css";

function Tabs() {
  return (
    <body>
      <div class="container">
        <div class="item">
          <h1 className="titleBar"> LOCOMOTION SYSTEM </h1>
          <div id="LOC_CANVAS_WRAPPER" className="canvasWrap">
            <canvas id="LOC_CANVAS" className="canvas"></canvas>
          </div>
          <h1 className="listElem one"> ROVER NAME: </h1>
          <h1 className="listElem two"> CONNECTION: </h1>
          <h1 className="listElem three"> IP ADDRESS: </h1>
          <h1 className="listElem four"> MEMORY: </h1>
        </div>
        <div class="item">
          <h1 className="titleBar"> LIDAR </h1>
          <button className="control button15" role="button">
            ACTION
          </button>
          <button className="control button16" role="button">
            ACTION
          </button>
          <button className="control button17" role="button">
            ACTION
          </button>
        </div>
        <div class="itembig">
          <h1 className="titleBar"> CAMERA </h1>
          <img src ="/video_feed" className="video"></img>
          <button className="control button6" role="button">
            ON
          </button>
          <button className="control button7" role="button">
            OFF
          </button>
          <button className="control button8" role="button">
            SCREENSHOT
          </button>
          <button className="control button81" role="button">
            LIGHTS ON
          </button>
          <button className="control button82" role="button">
            LIGHTS OFF
          </button>
          <button className="control button83" role="button">
            LIGHTS MAX
          </button>
        </div>
        <div class="item">
          <h1 className="titleBar"> HISTORY </h1>
          <button className="control button10" role="button">
            ACTION
          </button>
          <button className="control button11" role="button">
            ACTION
          </button>
        </div>
        <div class="itemlast">
          <h1 className="titleBar"> QUEUE </h1>
          <button className="control button12" role="button">
            ACTION
          </button>
          <button className="control button13" role="button">
            ACTION
          </button>
          <button className="control button14" role="button">
            ACTION
          </button>
        </div>
      </div>
      <div class="container2">
        <div class="item2">
          <button className="controlButton1" role="button">
            &#8593;
          </button>
          <button className="controlButton2" role="button">
            &#8594;
          </button>
          <button className="controlButton3" role="button">
            &#8595;
          </button>
          <button className="controlButton4" role="button">
            &#8592;
          </button>
        </div>
        <div class="item2big">
          {/* <h1 className="titleBar"> GEOGRAPHICAL PAYLOADS </h1> */}
          <h2 className="titleBar subtitleOne"> GEOPHONE </h2>
          <h2 className="titleBar subtitleTwo"> HUMIDITY </h2>
          <h2 className="titleBar subtitleThree"> PRESSURE </h2>
          <h2 className="titleBar subtitleFour"> WIND </h2>
        </div>
        <div class="item2last">
          <button className="controlButton5" role="button">
            STOP
          </button>
          <button className="controlButton6" role="button">
            TURN ON
          </button>
          <button className="controlButton7" role="button">
            TURN OFF
          </button>
          <button className="control button1" role="button">
            STAND UP
          </button>
          <button className="control button2" role="button">
            LIE DOWN
          </button>
          <button className="control button3" role="button">
            SIT
          </button>
          <button className="control button4" role="button">
            BOW
          </button>
          <button className="control button5" role="button">
            RELAX
          </button>
        </div>
      </div>
    </body>
  );
}
export default Tabs;
