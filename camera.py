def update_camera(camera, player, window, world_width: int, world_height: int) -> None:
    LEFT_MARGIN = 200
    RIGHT_MARGIN = 200
    BOTTOM_MARGIN = 200
    TOP_MARGIN = 200

    cam_cx, cam_cy = camera.position
    w = window.width
    h = window.height

    cam_left = cam_cx - w / 2
    cam_bottom = cam_cy - h / 2

    left_boundary = cam_left + LEFT_MARGIN
    right_boundary = cam_left + w - RIGHT_MARGIN
    bottom_boundary = cam_bottom + BOTTOM_MARGIN
    top_boundary = cam_bottom + h - TOP_MARGIN

    if player.left < left_boundary:
        cam_left = player.left - LEFT_MARGIN
    elif player.right > right_boundary:
        cam_left = player.right - (w - RIGHT_MARGIN)

    if player.bottom < bottom_boundary:
        cam_bottom = player.bottom - BOTTOM_MARGIN
    elif player.top > top_boundary:
        cam_bottom = player.top - (h - TOP_MARGIN)

    max_left = max(0, world_width - w)
    max_bottom = max(0, world_height - h)

    cam_left = min(max(cam_left, 0), max_left)
    cam_bottom = min(max(cam_bottom, 0), max_bottom)

    camera.position = (cam_left + w / 2, cam_bottom + h / 2)
