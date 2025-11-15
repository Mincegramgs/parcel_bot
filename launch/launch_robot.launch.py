import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription,  DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

from launch_ros.actions import Node



def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='parcel_bot' #<--- CHANGE ME

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false'}.items()
    )

    # joystick = IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource([os.path.join(
    #                 get_package_share_directory(package_name),'launch','joystick.launch.py'
    #             )])
    # )


    # twist_mux_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux.yaml')
    # twist_mux = Node(
    #         package="twist_mux",
    #         executable="twist_mux",
    #         parameters=[twist_mux_params],
    #         remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')]
    #     )
    
    ekf_config = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'ekf.yaml'
    )

    laser_scan_filter = Node(
        package='laser_scan_filter',
        executable='laser_filter',
        name='laser_scan_node',
        output ='screen',
        parameters=[{'use_sim_time': False}]
    )
    
    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': False}]
    )

    camera_node = Node(
        package='camera_ros',
        executable='camera_node',
        name='camera',
        output='screen',
        parameters=[{'use_sim_time': False}]
    )

    imu_filter_node = Node(
        package= 'imu_filter',
        executable='imu_filter',
        name='imu_node',
        output ='screen',
        parameters=[{'use_sim_time': False}]

    )

    
    robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])

    channel_type = LaunchConfiguration('channel_type', default='serial')
    serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    serial_baudrate = LaunchConfiguration('serial_baudrate', default='115200')
    frame_id = LaunchConfiguration('frame_id', default='laser')
    inverted = LaunchConfiguration('inverted', default='false')
    angle_compensate = LaunchConfiguration('angle_compensate', default='true')
    scan_mode = LaunchConfiguration('scan_mode', default='Sensitivity')

    lidar_node = Node(
        package='sllidar_ros2',
        executable='sllidar_node',
        name='sllidar_node',
        output='screen',
        parameters=[{
            'channel_type': channel_type,
            'serial_port': serial_port,
            'serial_baudrate': serial_baudrate,
            'frame_id': frame_id,
            'inverted': inverted,
            'angle_compensate': angle_compensate,
            'scan_mode': scan_mode
        }]
    )
    rviz_config_path = os.path.join(
        get_package_share_directory('sllidar_ros2'),
        'rviz',
        'sllidar_ros2.rviz'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )

    # === 6. Add Delays (TimerAction) ===
    # Delay LiDAR startup by 5 seconds
    delayed_lidar = TimerAction(
        period=5.0,
        actions=[lidar_node]
    )

    # Delay RViz startup by 8 seconds (after TF, LiDAR, and robot model are ready)
    delayed_rviz = TimerAction(
        period=8.0,
        actions=[rviz_node]
    )

    # === 7. Declare Arguments ===
    declare_args = [
        DeclareLaunchArgument('channel_type', default_value='serial'),
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('serial_baudrate', default_value='115200'),
        DeclareLaunchArgument('frame_id', default_value='laser'),
        DeclareLaunchArgument('inverted', default_value='false'),
        DeclareLaunchArgument('angle_compensate', default_value='true'),
        DeclareLaunchArgument('scan_mode', default_value='Sensitivity'),
    ]
    # controller_params_file = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')

    # controller_manager = Node(
    #     package="controller_manager",
    #     executable="ros2_control_node",
    #     parameters=[{'robot_description': robot_description},
    #                 controller_params_file]
    # )

    # delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

    # diff_drive_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["diff_cont"],
    # )

    # delayed_diff_drive_spawner = RegisterEventHandler(
    #     event_handler=OnProcessStart(
    #         target_action=controller_manager,
    #         on_start=[diff_drive_spawner],
    #     )
    # )

    # joint_broad_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["joint_broad"],
    # )

    # delayed_joint_broad_spawner = RegisterEventHandler(
    #     event_handler=OnProcessStart(
    #         target_action=controller_manager,
    #         on_start=[joint_broad_spawner],
    #     )
    # )


    # Code for delaying a node (I haven't tested how effective it is)
    # 
    # First add the below lines to imports
    # from launch.actions import RegisterEventHandler
    # from launch.event_handlers import OnProcessExit
    #
    # Then add the following below the current diff_drive_spawner
    # delayed_diff_drive_spawner = RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=spawn_entity,
    #         on_exit=[diff_drive_spawner],
    #     )
    # )
    #
    # Replace the diff_drive_spawner in the final return with delayed_diff_drive_spawner



    # Launch them all!
    return LaunchDescription([
        *declare_args,
        rsp,
        robot_localization_node,
        # camera_node,
        imu_filter_node,
        delayed_lidar,
        laser_scan_filter
        # delayed_rviz
        # joystick,
        # twist_mux,
        # delayed_controller_manager,
        # delayed_diff_drive_spawner,
        # delayed_joint_broad_spawner
    ])
