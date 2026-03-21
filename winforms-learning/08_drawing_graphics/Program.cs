// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WinForms 08 - 그리기와 그래픽스 (Drawing & Graphics)  ■
// ■  간단한 그림판 만들기                                   ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일에서 배우는 것:
//   1) Paint 이벤트    - 화면을 다시 그려야 할 때 발생하는 신호
//   2) Graphics 객체   - 도화지에 그림을 그리는 도구 (붓, 연필 세트)
//   3) Pen            - 선을 그리는 펜 (색, 굵기 설정)
//   4) Brush          - 도형 안을 채우는 붓 (색칠 도구)
//   5) DrawLine       - 직선 그리기
//   6) DrawRectangle  - 사각형 그리기 (테두리만)
//   7) FillEllipse    - 원/타원 채우기 (색칠까지)
//   8) DrawString     - 글자 그리기
//   9) 더블 버퍼링     - 깜빡임 없이 부드럽게 그리기

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new DrawingForm());
    }
}

// ┌──────────────────────────────────────────────────┐
// │  그려진 도형 하나를 저장하는 클래스                 │
// └──────────────────────────────────────────────────┘
// 그림판에서 그린 각 선은 "시작점 → 끝점"으로 이루어집니다.
// 연필로 종이에 선을 긋는 것처럼, 어디서 시작해서 어디서 끝났는지 기록합니다.
public class DrawnLine
{
    public Point Start { get; set; }
    public Point End { get; set; }
    public Color LineColor { get; set; }
    public float Thickness { get; set; }
}

// ┌──────────────────────────────────────────────────┐
// │  그림판 폼 - Paint 이벤트와 Graphics 활용         │
// └──────────────────────────────────────────────────┘
public sealed class DrawingForm : Form
{
    private readonly List<DrawnLine> _lines = new List<DrawnLine>();
    private readonly Panel _canvas;
    private Point _lastPoint;
    private bool _isDrawing;
    private Color _currentColor = Color.Black;
    private float _currentThickness = 3f;
    private readonly Label _statusLabel;

    public DrawingForm()
    {
        Text = "미니 그림판 - Graphics 학습";
        Size = new Size(800, 600);
        StartPosition = FormStartPosition.CenterScreen;

        // ┌──────────────────────────────────────────┐
        // │  더블 버퍼링 (Double Buffering)            │
        // └──────────────────────────────────────────┘
        // 더블 버퍼링은 "두 장의 종이" 기법입니다.
        // 1) 뒤쪽 종이에 그림을 완성하고
        // 2) 완성된 그림을 앞쪽에 한 번에 보여줍니다.
        // 이렇게 하면 그리는 과정이 안 보여서 깜빡임이 없어요!
        // 만화영화도 같은 원리: 그림을 빠르게 바꿔서 부드럽게 보이게 합니다.

        // ── 도구 모음 ──
        var toolStrip = new ToolStrip();

        // 색상 버튼들
        var colors = new[]
        {
            ("검정", Color.Black), ("빨강", Color.Red),
            ("파랑", Color.Blue), ("초록", Color.Green),
            ("주황", Color.Orange), ("보라", Color.Purple)
        };
        foreach (var (name, color) in colors)
        {
            var btn = new ToolStripButton(name);
            btn.ForeColor = color;
            btn.Font = new Font("맑은 고딕", 9, FontStyle.Bold);
            Color capturedColor = color; // 클로저를 위한 캡처
            btn.Click += (s, e) =>
            {
                _currentColor = capturedColor;
                _statusLabel.Text = $"색상: {name}";
            };
            toolStrip.Items.Add(btn);
        }

        toolStrip.Items.Add(new ToolStripSeparator());

        // 굵기 선택
        toolStrip.Items.Add(new ToolStripLabel("굵기:"));
        var thicknessCombo = new ToolStripComboBox();
        thicknessCombo.Items.AddRange(new object[] { "1", "2", "3", "5", "8", "12" });
        thicknessCombo.SelectedIndex = 2;
        thicknessCombo.SelectedIndexChanged += (s, e) =>
        {
            if (float.TryParse(thicknessCombo.Text, out float t))
                _currentThickness = t;
        };
        toolStrip.Items.Add(thicknessCombo);

        toolStrip.Items.Add(new ToolStripSeparator());

        // 지우기 버튼
        var clearBtn = new ToolStripButton("전체 지우기");
        clearBtn.Click += (s, e) =>
        {
            _lines.Clear();
            _canvas.Invalidate(); // 다시 그리기 요청
            _statusLabel.Text = "캔버스를 지웠습니다.";
        };
        toolStrip.Items.Add(clearBtn);

        // 도형 그리기 예제 버튼
        var shapeBtn = new ToolStripButton("도형 예제");
        shapeBtn.Click += (s, e) =>
        {
            _lines.Clear();
            _canvas.Invalidate();
            _statusLabel.Text = "도형 예제가 그려집니다.";
        };
        shapeBtn.Tag = "shapes";
        toolStrip.Items.Add(shapeBtn);

        // ┌──────────────────────────────────────────┐
        // │  캔버스 패널 - 그림을 그리는 도화지         │
        // └──────────────────────────────────────────┘
        _canvas = new Panel
        {
            Dock = DockStyle.Fill,
            BackColor = Color.White
        };

        // ── 더블 버퍼링 활성화 ──
        // Panel에 더블 버퍼링을 적용하려면 리플렉션을 사용합니다.
        typeof(Panel).InvokeMember("DoubleBuffered",
            System.Reflection.BindingFlags.SetProperty |
            System.Reflection.BindingFlags.Instance |
            System.Reflection.BindingFlags.NonPublic,
            null, _canvas, new object[] { true });

        // ┌──────────────────────────────────────────┐
        // │  Paint 이벤트 - 화면 그리기                │
        // └──────────────────────────────────────────┘
        // Paint 이벤트는 "화면을 다시 그려주세요!" 라는 신호입니다.
        // 창을 움직이거나, 다른 창에 가렸다가 다시 보이면 발생합니다.
        // 칠판을 닦고 다시 쓰는 것처럼, 매번 처음부터 그립니다.
        _canvas.Paint += Canvas_Paint;

        // ┌──────────────────────────────────────────┐
        // │  마우스 이벤트 - 그림 그리기 동작           │
        // └──────────────────────────────────────────┘
        // MouseDown: 마우스 버튼을 누름 → 그리기 시작
        // MouseMove: 마우스를 움직임 → 선을 그림
        // MouseUp:   마우스 버튼을 놓음 → 그리기 끝
        // 연필을 종이에 대고(Down), 움직이며 선을 긋고(Move), 떼는(Up) 과정!

        _canvas.MouseDown += (s, e) =>
        {
            if (e.Button == MouseButtons.Left)
            {
                _isDrawing = true;
                _lastPoint = e.Location;
            }
        };

        _canvas.MouseMove += (s, e) =>
        {
            if (_isDrawing)
            {
                // 작은 선분들을 이어서 부드러운 곡선처럼 보이게 합니다.
                // 점을 빽빽하게 찍어서 선처럼 보이게 하는 점묘법과 비슷해요!
                _lines.Add(new DrawnLine
                {
                    Start = _lastPoint,
                    End = e.Location,
                    LineColor = _currentColor,
                    Thickness = _currentThickness
                });
                _lastPoint = e.Location;
                _canvas.Invalidate(); // 화면 갱신 요청
            }
        };

        _canvas.MouseUp += (s, e) =>
        {
            _isDrawing = false;
        };

        // 상태 표시줄
        var statusStrip = new StatusStrip();
        _statusLabel = new ToolStripStatusLabel("마우스로 캔버스에 그림을 그려보세요!")
        {
            Spring = true
        };
        statusStrip.Items.Add(_statusLabel);

        Controls.Add(_canvas);
        Controls.Add(toolStrip);
        Controls.Add(statusStrip);
    }

    // ┌──────────────────────────────────────────┐
    // │  Paint 이벤트 핸들러                       │
    // └──────────────────────────────────────────┘
    private void Canvas_Paint(object? sender, PaintEventArgs e)
    {
        // Graphics 객체는 "그림 도구 세트"입니다.
        // 이 도구로 선, 사각형, 원, 글자를 그릴 수 있습니다.
        Graphics g = e.Graphics;

        // ── 품질 설정 ──
        // AntiAlias는 계단 현상(울퉁불퉁한 선)을 부드럽게 합니다.
        // 저화질 사진 vs 고화질 사진의 차이와 같아요!
        g.SmoothingMode = SmoothingMode.AntiAlias;

        // ── 사용자가 그린 선들 그리기 ──
        foreach (var line in _lines)
        {
            // Pen은 선을 그리는 펜입니다. 색상과 굵기를 지정합니다.
            using var pen = new Pen(line.LineColor, line.Thickness)
            {
                StartCap = LineCap.Round,  // 선 시작 부분을 둥글게
                EndCap = LineCap.Round      // 선 끝 부분을 둥글게
            };
            g.DrawLine(pen, line.Start, line.End);
        }

        // ── 도형 예제 (lines가 비어있으면 기본 도형 표시) ──
        if (_lines.Count == 0)
        {
            DrawShapeExamples(g);
        }
    }

    // ┌──────────────────────────────────────────┐
    // │  도형 그리기 예제 모음                      │
    // └──────────────────────────────────────────┘
    private void DrawShapeExamples(Graphics g)
    {
        int x = 20, y = 20;

        // ── DrawString: 글자 그리기 ──
        // 도화지에 글자를 적는 것과 같습니다.
        // Font = 글씨체, Brush = 글자 색
        using (var titleFont = new Font("맑은 고딕", 16, FontStyle.Bold))
        using (var brush = new SolidBrush(Color.DarkSlateGray))
        {
            g.DrawString("Graphics 도형 예제", titleFont, brush, x, y);
        }
        y += 45;

        // ── DrawLine: 직선 그리기 ──
        // Pen(색상, 굵기)으로 두 점 사이에 선을 긋습니다.
        using (var pen = new Pen(Color.Red, 3))
        {
            g.DrawLine(pen, x, y, x + 200, y);
        }
        using (var font = new Font("맑은 고딕", 9))
        {
            g.DrawString("DrawLine - 직선", font, Brushes.Gray, x + 210, y - 8);
        }
        y += 30;

        // ── DrawRectangle: 사각형 테두리 ──
        // 네 꼭짓점을 연결해서 사각형을 그립니다 (안은 비어있음).
        using (var pen = new Pen(Color.Blue, 2))
        {
            g.DrawRectangle(pen, x, y, 150, 60);
        }
        g.DrawString("DrawRectangle", new Font("맑은 고딕", 9), Brushes.Gray, x + 160, y + 20);
        y += 80;

        // ── FillRectangle: 사각형 채우기 ──
        // SolidBrush로 안쪽까지 색칠합니다.
        // 선으로 테두리만 그리는 것(Draw) vs 색연필로 칠하는 것(Fill)
        using (var brush = new SolidBrush(Color.LightBlue))
        {
            g.FillRectangle(brush, x, y, 150, 60);
        }
        using (var pen = new Pen(Color.DarkBlue, 2))
        {
            g.DrawRectangle(pen, x, y, 150, 60);
        }
        g.DrawString("FillRectangle", new Font("맑은 고딕", 9), Brushes.Gray, x + 160, y + 20);
        y += 80;

        // ── FillEllipse: 원/타원 채우기 ──
        // 타원은 사각형 안에 꼭 맞게 들어가는 동그라미입니다.
        // 정사각형이면 완벽한 원, 직사각형이면 타원이 됩니다.
        using (var brush = new SolidBrush(Color.LightGreen))
        {
            g.FillEllipse(brush, x, y, 100, 100); // 정사각형 → 원
        }
        using (var pen = new Pen(Color.DarkGreen, 2))
        {
            g.DrawEllipse(pen, x, y, 100, 100);
        }
        g.DrawString("FillEllipse - 원", new Font("맑은 고딕", 9), Brushes.Gray, x + 110, y + 40);

        // 오른쪽 열에 추가 도형
        int rx = 350;
        int ry = 70;

        // ── 그라데이션 브러시 ──
        // LinearGradientBrush는 한 색에서 다른 색으로 서서히 변합니다.
        // 일출 때 하늘이 빨강→주황→노랑으로 변하는 것처럼!
        var gradRect = new Rectangle(rx, ry, 180, 80);
        using (var gradBrush = new LinearGradientBrush(
            gradRect, Color.Orange, Color.Purple, LinearGradientMode.Horizontal))
        {
            g.FillRectangle(gradBrush, gradRect);
        }
        g.DrawString("그라데이션 브러시", new Font("맑은 고딕", 9), Brushes.Gray, rx, ry + 85);
        ry += 115;

        // ── 대시(점선) 스타일 ──
        // DashStyle로 점선, 파선 등 다양한 선 스타일을 적용합니다.
        using (var dashPen = new Pen(Color.DarkRed, 2) { DashStyle = DashStyle.Dash })
        {
            g.DrawRectangle(dashPen, rx, ry, 180, 60);
        }
        g.DrawString("점선 스타일 (DashStyle)", new Font("맑은 고딕", 9), Brushes.Gray, rx, ry + 65);
        ry += 95;

        // ── 여러 도형 조합 ──
        // 간단한 집 그리기
        g.DrawString("조합 예제: 집", new Font("맑은 고딕", 10, FontStyle.Bold), Brushes.Black, rx, ry);
        ry += 25;
        g.FillRectangle(Brushes.Khaki, rx + 30, ry + 40, 120, 80);       // 집 몸통
        g.DrawRectangle(Pens.SaddleBrown, rx + 30, ry + 40, 120, 80);
        // 지붕 (삼각형 = 다각형의 일종)
        g.FillPolygon(Brushes.IndianRed, new[]
        {
            new Point(rx + 20, ry + 40),
            new Point(rx + 90, ry),
            new Point(rx + 160, ry + 40)
        });
        // 문
        g.FillRectangle(Brushes.SaddleBrown, rx + 70, ry + 80, 40, 40);
        // 창문
        g.FillRectangle(Brushes.LightCyan, rx + 40, ry + 55, 25, 25);
        g.DrawRectangle(Pens.Gray, rx + 40, ry + 55, 25, 25);
    }
}
