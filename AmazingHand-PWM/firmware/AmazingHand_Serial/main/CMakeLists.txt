idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES esp_timer hand_protocol hand_gestures hand_servo
)
