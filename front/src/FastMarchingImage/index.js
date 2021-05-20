import { Button, Input, Space } from 'antd'
import { useEffect, useRef, useState } from 'react'

const clearCanvas = (ctx) => ctx.clearRect(0, 0, 1000, 1000)

const drawCross = (ctx) => (point) => {
  ctx.beginPath()
  ctx.lineWidth = 2
  ctx.lineCap = 'round'

  ctx.moveTo(point.x - 5, point.y - 5)
  ctx.lineTo(point.x + 5, point.y + 5)

  ctx.moveTo(point.x - 5, point.y + 5)
  ctx.lineTo(point.x + 5, point.y - 5)

  ctx.strokeStyle = '#FF0000'
  ctx.stroke()
}

const drawImage = (ctx, file) => {
  const img = new Image()
  img.src = URL.createObjectURL(file)
  img.addEventListener('load', () => {
    ctx.drawImage(img, 0, 0, img.width, img.height)
  })
}

function FastMarchingImage() {
  const canvasRef = useRef(null)
  const [file, setFile] = useState()
  const [points, setPoints] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const ctx = canvasRef.current?.getContext('2d')

    if (!ctx) {
      return
    }

    if (points.length) {
      points.forEach(drawCross(ctx))
    } else {
      clearCanvas(ctx)
      drawImage(ctx, file)
    }
  }, [file, points])

  return (
    <div>
      <Space direction="vertical">
        <Input
          type="file"
          onChange={({
            target: {
              files: [file],
            },
          }) => {
            if (file) {
              setPoints([])
              setFile(file)
            }
          }}
        />

        <Space>
          <Button onClick={() => setPoints([])}>Recommencer</Button>
          <Button
            type="primary"
            loading={loading}
            onClick={() => {
              setLoading(true)

              const data = new FormData()
              data.append('file', file)
              data.append(
                'rawPoints',
                points.map((p) => `${p.x},${p.y}`).join(';')
              )

              console.log(points.map((p) => `${p.x},${p.y}`).join(';'))

              fetch('http://localhost:8000/files', {
                method: 'POST',
                body: data,
              })
                .then((res) => res.json())
                .then(({ curves }) => {
                  const ctx = canvasRef.current?.getContext('2d')

                  ctx.beginPath()
                  ctx.lineWidth = 2

                  for (const curve of curves) {
                    for (const [y, x] of curve) {
                      ctx.moveTo(x, y)
                      ctx.lineTo(x, y)
                    }
                  }

                  ctx.strokeStyle = '#FF0000'
                  ctx.stroke()
                })
                .catch(console.error)
                .finally(() => setLoading(false))
            }}
          >
            valider
          </Button>
        </Space>

        {file && (
          <div>
            <canvas
              ref={canvasRef}
              width="1000"
              height="1000"
              onClick={(event) => {
                const imageRect = canvasRef.current?.getBoundingClientRect()

                const x = event.clientX - imageRect.left
                const y = event.clientY - imageRect.top

                setPoints([...points, { x, y }])
              }}
            />
          </div>
        )}
      </Space>
    </div>
  )
}

export default FastMarchingImage
