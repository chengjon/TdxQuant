#include <Keyboard.h>

static String readLine() {
  String line = "";
  while (Serial.available() > 0) {
    char ch = (char)Serial.read();
    if (ch == '\r') {
      continue;
    }
    if (ch == '\n') {
      break;
    }
    line += ch;
  }
  return line;
}

static void tapKey(uint8_t keycode, unsigned long holdMs = 40) {
  Keyboard.press(keycode);
  delay(holdMs);
  Keyboard.release(keycode);
  delay(holdMs);
}

static void tapCtrlA() {
  Keyboard.press(KEY_LEFT_CTRL);
  Keyboard.press('a');
  delay(50);
  Keyboard.releaseAll();
  delay(50);
}

static bool handleKeyCommand(const String& keyName) {
  if (keyName == "TAB") {
    tapKey(KEY_TAB);
    return true;
  }
  if (keyName == "ENTER") {
    tapKey(KEY_RETURN);
    return true;
  }
  if (keyName == "ESC") {
    tapKey(KEY_ESC);
    return true;
  }
  if (keyName == "DELETE") {
    tapKey(KEY_DELETE);
    return true;
  }
  if (keyName == "CTRL+A") {
    tapCtrlA();
    return true;
  }
  return false;
}

static void handleTypeCommand(const String& payload, const String& trailingKey) {
  for (unsigned int i = 0; i < payload.length(); ++i) {
    char ch = payload.charAt(i);
    if (ch < '0' || ch > '9') {
      Serial.println("ERR TYPE_ONLY_DIGITS");
      return;
    }
    Keyboard.press(ch);
    delay(40);
    Keyboard.release(ch);
    delay(40);
  }
  if (trailingKey.length() > 0) {
    if (!handleKeyCommand(trailingKey)) {
      Serial.println("ERR UNKNOWN_KEY");
      return;
    }
  }
  Serial.print("OK TYPE ");
  Serial.println(payload);
}

void setup() {
  Serial.begin(115200);
  Keyboard.begin();
}

void loop() {
  if (Serial.available() <= 0) {
    delay(10);
    return;
  }

  String line = readLine();
  line.trim();
  if (line.length() == 0) {
    return;
  }

  if (line == "PING") {
    Serial.println("OK PONG");
    return;
  }

  if (line.startsWith("KEY ")) {
    String keyName = line.substring(4);
    keyName.trim();
    if (!handleKeyCommand(keyName)) {
      Serial.println("ERR UNKNOWN_KEY");
      return;
    }
    Serial.print("OK KEY ");
    Serial.println(keyName);
    return;
  }

  if (line.startsWith("TYPE ")) {
    int firstSpace = line.indexOf(' ', 5);
    String payload = "";
    String trailingKey = "";
    if (firstSpace < 0) {
      payload = line.substring(5);
    } else {
      payload = line.substring(5, firstSpace);
      trailingKey = line.substring(firstSpace + 1);
      trailingKey.trim();
    }
    payload.trim();
    if (payload.length() == 0) {
      Serial.println("ERR EMPTY_TYPE");
      return;
    }
    handleTypeCommand(payload, trailingKey);
    return;
  }

  Serial.println("ERR UNKNOWN_CMD");
}
