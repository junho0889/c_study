// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 10 - IValueConverter / IMultiValueConverter      ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// IValueConverter는 "통역사"입니다.
//   데이터(한국어) → 화면 표시(영어)로 번역합니다.
//   Convert:     데이터 → 화면 (순방향)
//   ConvertBack: 화면 → 데이터 (역방향, 양방향 바인딩 시)
//
// IMultiValueConverter는 "다국어 통역사"입니다.
//   여러 값을 한꺼번에 받아서 하나의 결과로 변환합니다.
//   키 + 몸무게 → BMI 계산 같은 것!

using System;
using System.Globalization;
using System.Windows;
using System.Windows.Data;
using System.Windows.Media;

namespace LessonWpf
{
    // ┌──────────────────────────────────────────────────┐
    // │  1. 섭씨 → 화씨 변환기                           │
    // └──────────────────────────────────────────────────┘
    // 공식: °F = °C × 9/5 + 32
    // 예: 100°C → 212°F (물의 끓는점)
    public class CelsiusToFahrenheitConverter : IValueConverter
    {
        public object Convert(object value, Type targetType,
            object parameter, CultureInfo culture)
        {
            if (double.TryParse(value?.ToString(), out double celsius))
            {
                double fahrenheit = celsius * 9.0 / 5.0 + 32;
                return $"{fahrenheit:F1} °F";
            }
            return "-- °F";
        }

        // ConvertBack: 화씨 → 섭씨 (역변환)
        // 양방향 바인딩이 아니면 구현하지 않아도 됩니다.
        public object ConvertBack(object value, Type targetType,
            object parameter, CultureInfo culture)
        {
            return DependencyProperty.UnsetValue;
        }
    }

    // ┌──────────────────────────────────────────────────┐
    // │  2. km → miles 변환기                             │
    // └──────────────────────────────────────────────────┘
    // 1 km = 0.621371 miles
    public class KmToMilesConverter : IValueConverter
    {
        public object Convert(object value, Type targetType,
            object parameter, CultureInfo culture)
        {
            if (double.TryParse(value?.ToString(), out double km))
            {
                double miles = km * 0.621371;
                return $"{miles:F2} miles";
            }
            return "-- miles";
        }

        public object ConvertBack(object value, Type targetType,
            object parameter, CultureInfo culture)
            => DependencyProperty.UnsetValue;
    }

    // ┌──────────────────────────────────────────────────┐
    // │  3. kg → lbs 변환기                               │
    // └──────────────────────────────────────────────────┘
    // 1 kg = 2.20462 lbs
    public class KgToLbsConverter : IValueConverter
    {
        public object Convert(object value, Type targetType,
            object parameter, CultureInfo culture)
        {
            if (double.TryParse(value?.ToString(), out double kg))
            {
                double lbs = kg * 2.20462;
                return $"{lbs:F2} lbs";
            }
            return "-- lbs";
        }

        public object ConvertBack(object value, Type targetType,
            object parameter, CultureInfo culture)
            => DependencyProperty.UnsetValue;
    }

    // ┌──────────────────────────────────────────────────┐
    // │  4. Bool → 텍스트 변환기                          │
    // └──────────────────────────────────────────────────┘
    // true → "활성", false → "비활성"
    // 신호등처럼: 초록불(true) = "가세요", 빨간불(false) = "멈추세요"
    public class BoolToTextConverter : IValueConverter
    {
        public object Convert(object value, Type targetType,
            object parameter, CultureInfo culture)
        {
            return (bool)value ? "활성 상태" : "비활성 상태";
        }

        public object ConvertBack(object value, Type targetType,
            object parameter, CultureInfo culture)
            => DependencyProperty.UnsetValue;
    }

    // ┌──────────────────────────────────────────────────┐
    // │  5. 숫자 → 색상 변환기                            │
    // └──────────────────────────────────────────────────┘
    // 점수에 따라 배경색이 변합니다:
    //   90~100 = 초록, 70~89 = 파랑, 50~69 = 주황, 0~49 = 빨강
    // 온도계가 온도에 따라 색이 변하는 것과 같아요!
    public class NumberToColorConverter : IValueConverter
    {
        public object Convert(object value, Type targetType,
            object parameter, CultureInfo culture)
        {
            if (int.TryParse(value?.ToString(), out int score))
            {
                return score switch
                {
                    >= 90 => new SolidColorBrush(Colors.Green),
                    >= 70 => new SolidColorBrush(Colors.RoyalBlue),
                    >= 50 => new SolidColorBrush(Colors.Orange),
                    _ => new SolidColorBrush(Colors.Red)
                };
            }
            return new SolidColorBrush(Colors.Gray);
        }

        public object ConvertBack(object value, Type targetType,
            object parameter, CultureInfo culture)
            => DependencyProperty.UnsetValue;
    }

    // ┌──────────────────────────────────────────────────┐
    // │  6. BMI 계산기 (IMultiValueConverter)             │
    // └──────────────────────────────────────────────────┘
    // IMultiValueConverter는 여러 값을 한꺼번에 받습니다.
    // 키(cm)와 몸무게(kg)를 받아서 BMI를 계산합니다.
    // 공식: BMI = 몸무게(kg) / 키(m)²
    // 요리사가 여러 재료(키, 몸무게)를 받아서 하나의 요리(BMI)를 만드는 것!
    public class BmiCalculatorConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType,
            object parameter, CultureInfo culture)
        {
            if (values.Length == 2 &&
                double.TryParse(values[0]?.ToString(), out double heightCm) &&
                double.TryParse(values[1]?.ToString(), out double weightKg) &&
                heightCm > 0)
            {
                double heightM = heightCm / 100.0;
                double bmi = weightKg / (heightM * heightM);

                string category = bmi switch
                {
                    < 18.5 => "저체중",
                    < 25.0 => "정상",
                    < 30.0 => "과체중",
                    _ => "비만"
                };

                return $"BMI: {bmi:F1} ({category})";
            }
            return "키와 몸무게를 입력하세요";
        }

        public object[] ConvertBack(object value, Type[] targetTypes,
            object parameter, CultureInfo culture)
        {
            return new object[] { DependencyProperty.UnsetValue, DependencyProperty.UnsetValue };
        }
    }
}
