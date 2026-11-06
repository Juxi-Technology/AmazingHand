idf_component_register(
    SRCS "hand_protocol.c"
    INCLUDE_DIRS "include"
    REQUIRES hand_gestures hand_servo
)
