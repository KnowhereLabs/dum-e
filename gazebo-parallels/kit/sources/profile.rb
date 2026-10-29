# Applies only to Gazebo simulation processes; never a global ld.so preload.
module GazeboVirglDefaults
  ROOT = File.realpath(File.dirname(__FILE__))
  LIBRARY = File.join(ROOT, 'libgazebo_virgl_defaults.so')
  ENGINE = File.join(ROOT, 'engine', 'libgz-rendering-ogre.so')
  MESA = File.join(ROOT, 'mesa')
  RENDER_OPTIONS = %w[--render-engine --render-engine-gui --render-engine-server
    --render-engine-api-backend --render-engine-gui-api-backend
    --render-engine-server-api-backend].freeze

  def self.enabled?
    ENV['GZ_VIRGL_DEFAULTS'] != '0'
  end

  def self.apply_environment!
    abort '[gazebo-defaults] Required profile library is missing.' unless File.readable?(LIBRARY)
    %w[LIBGL_ALWAYS_SOFTWARE GALLIUM_DRIVER MESA_GL_VERSION_OVERRIDE
       MESA_GLSL_VERSION_OVERRIDE LIBGL_ALWAYS_INDIRECT].each { |key| ENV.delete(key) }
    abort '[gazebo-defaults] Private rendering runtime is missing.' unless File.readable?(ENGINE) && File.directory?(File.join(MESA, 'dri'))
    ENV['LD_LIBRARY_PATH'] = ([MESA] + ENV.fetch('LD_LIBRARY_PATH', '').split(':')).uniq.join(':')
    ENV['LIBGL_DRIVERS_PATH'] = File.join(MESA, 'dri')
    ENV['GZ_VIRGL_RENDER_ENGINE'] = ENGINE
    ENV['QT_QPA_PLATFORM'] = 'xcb'
    ENV['DISPLAY'] = ':0' if ENV.fetch('DISPLAY', '').empty?
    if ENV.fetch('XAUTHORITY', '').empty?
      candidates = ["/run/user/#{Process.uid}/gdm/Xauthority", File.expand_path('~/.Xauthority')]
      authority = candidates.find { |path| File.readable?(path) }
      ENV['XAUTHORITY'] = authority if authority
    end
    preload = ENV.fetch('LD_PRELOAD', '').split(/[:\s]+/).reject(&:empty?)
    ENV['LD_PRELOAD'] = ([LIBRARY] + preload).uniq.join(':')
  end

  def self.sim_arguments(arguments)
    # Preserve arguments after an explicit option delimiter, including filenames.
    delimiter = arguments.index('--')
    before = delimiter ? arguments.take(delimiter) : arguments.dup
    after = delimiter ? arguments.drop(delimiter) : []
    result = []
    index = 0
    while index < before.size
      arg = before[index]
      if RENDER_OPTIONS.include?(arg)
        abort "[gazebo-defaults] Missing value for #{arg}" if index + 1 >= before.size
        index += 2
      elsif RENDER_OPTIONS.any? { |option| arg.start_with?(option + '=') }
        index += 1
      else
        result << arg
        index += 1
      end
    end
    result + ['--render-engine', ENGINE, '--render-engine-api-backend', 'opengl'] + after
  end
end
