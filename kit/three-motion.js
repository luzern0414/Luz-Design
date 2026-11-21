/* 空间层叠。由播放按钮启动，单次播放完成后恢复静态画面。 */
(() => {
  const runtimeUrl = new URL('vendor/three/three.min.js', document.currentScript.src);
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let runtime;

  function loadThree() {
    runtime ??= new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = runtimeUrl.href;
      script.onload = () => resolve(window.LzThree);
      script.onerror = () => reject(new Error('Three.js 加载失败'));
      document.head.appendChild(script);
    }).catch(error => {
      runtime = null;
      throw error;
    });
    return runtime;
  }

  function mount(demo) {
    const stage = demo.querySelector('.three-motion__stage');
    const still = demo.querySelector('.three-motion__still');
    const play = demo.querySelector('[data-three-play]');
    const status = demo.querySelector('[role="status"]');
    let active;

    function finish(message = '') {
      const previous = active;
      active = null;
      if (previous) {
        cancelAnimationFrame(previous.frame);
        previous.resize?.disconnect();
        previous.geometry?.dispose();
        previous.materials?.forEach(material => material.dispose());
        previous.renderer?.dispose();
        if (!previous.lost) previous.renderer?.forceContextLoss();
        previous.canvas?.remove();
      }
      still.hidden = false;
      play.disabled = reducedMotion.matches;
      play.removeAttribute('aria-disabled');
      status.textContent = message;
    }

    async function start() {
      if (active || reducedMotion.matches) return;
      const run = { frame: 0 };
      active = run;
      play.setAttribute('aria-disabled', 'true');
      status.textContent = '正在加载';
      try {
        const Three = await loadThree();
        if (active !== run) return;
        if (document.hidden || !stage.clientWidth) { finish(); return; }

        const canvas = document.createElement('canvas');
        const options = { alpha: true, antialias: true, powerPreference: 'low-power' };
        const context = canvas.getContext('webgl2', options);
        if (!context) { finish('已显示静态预览'); return; }
        run.canvas = canvas;
        canvas.addEventListener('webglcontextlost', () => {
          if (active !== run) return;
          run.lost = true;
          finish('已显示静态预览');
        });
        const renderer = run.renderer = new Three.WebGLRenderer({ ...options, canvas, context });
        const camera = new Three.OrthographicCamera(-2, 2, 1, -1, .1, 30);
        camera.position.set(1.2, 1.7, 5);
        camera.lookAt(0, 0, 0);
        const scene = new Three.Scene();
        const group = new Three.Group();
        const light = new Three.DirectionalLight(0xffffff, 2.2);
        light.position.set(2, 4, 5);
        scene.add(group, light, new Three.AmbientLight(0xffffff, 1.4));
        run.geometry = new Three.BoxGeometry(1.82, 1.08, .05);
        run.materials = [0x394d60, 0x829bb5, 0xc6d7e6].map(color => new Three.MeshLambertMaterial({ color }));
        const layers = run.materials.map(material => new Three.Mesh(run.geometry, material));
        group.add(...layers);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));

        function fit() {
          const width = stage.clientWidth;
          const height = stage.clientHeight;
          if (!width || !height) return;
          const aspect = width / height;
          const halfWidth = Math.max(2.25, 1.4 * aspect);
          camera.left = -halfWidth;
          camera.right = halfWidth;
          camera.top = halfWidth / aspect;
          camera.bottom = -camera.top;
          camera.updateProjectionMatrix();
          renderer.setSize(width, height, false);
        }
        let started;
        function draw(now) {
          started ??= now;
          const progress = Math.min(1, (now - started) / 950);
          const spread = Math.sin(progress * Math.PI) ** 2;
          group.rotation.y = -.15 + .22 * spread;
          group.rotation.x = -.07 - .09 * spread;
          layers.forEach((layer, index) => {
            const offset = index - 1;
            layer.position.set(offset * (.23 + .49 * spread), offset * (.14 + .08 * spread), offset * (.16 + .24 * spread));
          });
          renderer.render(scene, camera);
          if (progress < 1) run.frame = requestAnimationFrame(draw);
          else finish();
        }

        fit();
        stage.appendChild(canvas);
        still.hidden = true;
        status.textContent = '';
        run.resize = new ResizeObserver(fit);
        run.resize.observe(stage);
        run.frame = requestAnimationFrame(draw);
      } catch {
        if (active === run) finish('已显示静态预览');
      }
    }

    const watcher = new IntersectionObserver(([entry]) => {
      if (active && !entry.isIntersecting) finish();
    });
    watcher.observe(stage);
    document.addEventListener('visibilitychange', () => { if (document.hidden && active) finish(); });
    window.addEventListener('pagehide', () => finish());
    const syncPreference = () => finish(reducedMotion.matches ? '已显示静态预览' : '');
    reducedMotion.addEventListener('change', syncPreference);
    play.addEventListener('click', start);
    syncPreference();
  }

  document.querySelectorAll('[data-three-motion]').forEach(mount);
})();
