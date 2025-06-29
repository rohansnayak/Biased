#!/usr/bin/env python3
"""
Test script for the improved bias detection model
"""

from bias_model import PoliticalBiasAnalyzer
import json

def test_bias_detection():
    """Test the bias detection with various example articles"""
    
    analyzer = PoliticalBiasAnalyzer()
    
    # Test articles with different political leanings
    test_articles = [
        {
            'title': 'Left-leaning: Climate Change Article',
            'text': 'The climate crisis represents an existential threat to humanity that requires immediate and bold government action. The Green New Deal offers a comprehensive solution that would create millions of good-paying jobs while transitioning our economy to renewable energy. Fossil fuel companies must be held accountable for their role in environmental destruction, and we need progressive taxation to fund climate initiatives. Environmental justice communities, often low-income and communities of color, bear the brunt of pollution and climate impacts.',
            'expected': 'Left'
        },
        {
            'title': 'Right-leaning: Economic Policy Article',
            'text': 'The free market is the most efficient mechanism for allocating resources and creating prosperity. Government regulation stifles innovation and economic growth, while tax cuts for businesses and individuals stimulate the economy and create jobs. The private sector, not government, should drive economic recovery. Small government principles and fiscal responsibility are essential for long-term economic health. Corporate tax cuts will make America competitive again and bring jobs back from overseas.',
            'expected': 'Right'
        },
        {
            'title': 'Right-leaning: Social Issues Article',
            'text': 'Traditional family values are the foundation of a strong and prosperous society. Religious freedom must be protected from government overreach and secular attacks. The Second Amendment guarantees our fundamental right to bear arms for self-defense. Border security is essential for national security, and illegal immigration threatens American jobs and communities. Law and order policies are necessary to keep our streets safe from crime and chaos.',
            'expected': 'Right'
        },
        {
            'title': 'Left-leaning: Social Justice Article',
            'text': 'Systemic racism persists in our institutions and must be addressed through comprehensive police reform and criminal justice reform. Black Lives Matter activists are leading the charge for racial justice and equality. LGBTQ+ rights are fundamental human rights that deserve full protection under the law. Reproductive rights are essential for gender equality and women\'s autonomy. Immigration reform must provide a path to citizenship for Dreamers and undocumented immigrants.',
            'expected': 'Left'
        },
        {
            'title': 'Center: Balanced Analysis',
            'text': 'This bipartisan legislation represents a compromise that addresses concerns from both sides of the aisle. The data shows mixed results on the effectiveness of the policy, with some studies supporting it and others showing limited impact. Further research is needed to determine the long-term economic and social impacts. Experts disagree on the best approach to this complex issue, highlighting the need for continued dialogue and evidence-based policymaking.',
            'expected': 'Center'
        },
        {
            'title': 'Loaded Language: Right-leaning',
            'text': 'The radical left socialist agenda threatens to destroy American capitalism and freedom. This outrageous proposal would bankrupt our nation and lead to economic disaster. The corrupt establishment continues to ignore the will of the people, while dishonest politicians betray American values and sell out to special interests. These dangerous policies must be stopped before they destroy our way of life.',
            'expected': 'Right'
        },
        {
            'title': 'Loaded Language: Left-leaning',
            'text': 'The courageous activists are fighting against systemic oppression and injustice. Their brave stand for equality and justice inspires millions around the world. The greedy corporations are exploiting workers and destroying the environment for profit, while selfish billionaires refuse to pay their fair share in taxes. This revolutionary movement will bring about positive change for all Americans.',
            'expected': 'Left'
        },
        {
            'title': 'Left: Economic Inequality',
            'text': 'Rising income inequality is a threat to democracy. The wealthy 1% continue to amass fortunes while working families struggle to make ends meet. Progressive tax reform and a living wage are essential to restore fairness.',
            'expected': 'Left'
        },
        {
            'title': 'Right: Immigration Policy',
            'text': 'America must secure its borders and enforce immigration laws. Illegal immigration puts a strain on public resources and undermines national security. We need strong border enforcement and merit-based immigration.',
            'expected': 'Right'
        },
        {
            'title': 'Center: Factual Science Reporting',
            'text': 'A new study published in Nature found that the vaccine was 95% effective in preventing disease. Researchers caution that more data is needed to assess long-term effects. The findings have been peer-reviewed.',
            'expected': 'Center'
        },
        {
            'title': 'Left: Climate Protest',
            'text': 'Thousands of activists marched in the city center demanding urgent action on climate change. Protesters called for a transition to renewable energy and criticized government inaction on environmental issues.',
            'expected': 'Left'
        },
        {
            'title': 'Right: Gun Rights',
            'text': 'The Second Amendment guarantees Americans the right to bear arms. Gun control measures threaten our freedom and do little to stop criminals. Law-abiding citizens must be able to defend themselves.',
            'expected': 'Right'
        },
        {
            'title': 'Center: International Diplomacy',
            'text': 'Leaders from both countries met to discuss trade agreements and regional security. The talks were described as constructive, with both sides agreeing to continue dialogue.',
            'expected': 'Center'
        },
        {
            'title': 'Ambiguous: Economic Growth',
            'text': 'The economy grew by 3% last quarter, driven by strong consumer spending and business investment. Unemployment remains low, but some analysts warn of potential inflation risks.',
            'expected': 'Center'
        },
        {
            'title': 'Left: Healthcare Access',
            'text': 'Healthcare is a human right. No one should go bankrupt because they get sick. Universal healthcare would ensure everyone has access to the care they need, regardless of income.',
            'expected': 'Left'
        },
        {
            'title': 'Right: Tax Cuts',
            'text': 'Tax cuts have spurred economic growth and put more money in the pockets of hardworking Americans. Lower taxes encourage investment and job creation.',
            'expected': 'Right'
        },
        {
            'title': 'Tricky: Left Source, Neutral Tone',
            'text': 'The city council passed a new budget after weeks of debate. The budget includes funding for infrastructure, education, and public safety. Officials say the process was collaborative.',
            'expected': 'Center'
        },
        {
            'title': 'Tricky: Right Source, Neutral Tone',
            'text': 'The governor signed a bill updating the state\'s transportation regulations. The new law aims to improve road safety and reduce traffic congestion.',
            'expected': 'Center'
        },
        {
            'title': 'International: UK Labour Party',
            'text': 'The Labour Party unveiled a plan to increase funding for the National Health Service and raise the minimum wage. Critics argue the proposals would increase government spending.',
            'expected': 'Left'
        },
        {
            'title': 'International: UK Conservative Party',
            'text': 'The Conservative Party pledged to cut taxes and reduce government debt. The party also promised to strengthen border controls and invest in national defense.',
            'expected': 'Right'
        },
        {
            'title': 'International: French Politics',
            'text': 'President Macron called for unity and reform in the face of economic challenges. The government plans to balance fiscal responsibility with social protections.',
            'expected': 'Center'
        },
        {
            'title': 'Loaded Language: Both Sides',
            'text': 'The radical left is pushing a dangerous socialist agenda that threatens our freedoms, while the far right continues to spread hate and division. Only a centrist approach can save the country from disaster.',
            'expected': 'Center'
        },
        {
            'title': 'Subtle: Environmental Policy',
            'text': 'The administration announced new regulations to reduce carbon emissions. Supporters say the rules will help fight climate change, while opponents argue they will hurt the economy.',
            'expected': 'Center'
        },
        {
            'title': 'Subtle: Policing',
            'text': 'Police departments across the country are adopting new training programs. Advocates hope these changes will improve community relations and reduce incidents of misconduct.',
            'expected': 'Center'
        },
        {
            'title': 'Left: Social Justice',
            'text': 'Activists are calling for an end to systemic racism and police brutality. The movement seeks justice for marginalized communities and reforms to the criminal justice system.',
            'expected': 'Left'
        },
        {
            'title': 'Right: Religious Freedom',
            'text': 'Religious freedom is under attack by government overreach. People of faith must be allowed to practice their beliefs without interference from the state.',
            'expected': 'Right'
        },
        {
            'title': 'Center: Data-Driven Reporting',
            'text': 'According to the latest census data, the population has grown steadily over the past decade. Experts attribute the growth to a combination of immigration and higher birth rates.',
            'expected': 'Center'
        }
    ]
    
    print("🧪 Testing Bias Detection Model")
    print("=" * 60)
    
    results = []
    correct = 0
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n📰 Test {i}: {article['title']}")
        print("-" * 40)
        
        # Analyze the article
        score, label, details = analyzer.classify_bias(article['text'])
        
        # Check if prediction matches expected
        is_correct = label == article['expected']
        if is_correct:
            correct += 1
        
        print(f"Expected: {article['expected']}")
        print(f"Predicted: {label} (score: {score:.3f})")
        print(f"Confidence: {details.get('confidence', 'unknown')}")
        print(f"Result: {'✅ CORRECT' if is_correct else '❌ INCORRECT'}")
        
        # Show detailed breakdown
        print(f"  - Keyword analysis: {details.get('keyword_label', 'N/A')} ({details.get('keyword_score', 0):.3f})")
        print(f"  - Sentiment analysis: {details.get('sentiment_label', 'N/A')} ({details.get('sentiment_score', 0):.3f})")
        print(f"  - Loaded language: {details.get('loaded_label', 'N/A')} ({details.get('loaded_score', 0):.3f})")
        
        results.append({
            'test': i,
            'title': article['title'],
            'expected': article['expected'],
            'predicted': label,
            'score': score,
            'correct': is_correct,
            'details': details
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(test_articles)}")
    print(f"Correct predictions: {correct}")
    print(f"Accuracy: {correct/len(test_articles)*100:.1f}%")
    
    # Show breakdown by expected bias
    bias_counts = {}
    for result in results:
        expected = result['expected']
        if expected not in bias_counts:
            bias_counts[expected] = {'total': 0, 'correct': 0}
        bias_counts[expected]['total'] += 1
        if result['correct']:
            bias_counts[expected]['correct'] += 1
    
    print("\n📈 Breakdown by Expected Bias:")
    for bias, counts in bias_counts.items():
        accuracy = counts['correct'] / counts['total'] * 100
        print(f"  {bias}: {counts['correct']}/{counts['total']} ({accuracy:.1f}%)")
    
    # Save detailed results
    with open('bias_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: bias_test_results.json")
    
    return results

def test_custom_article():
    """Test with a custom article from user input"""
    analyzer = PoliticalBiasAnalyzer()
    
    print("\n🎯 Test Custom Article")
    print("=" * 40)
    
    # Get article text from user
    print("Enter article text (or press Enter to use a sample):")
    article_text = input().strip()
    
    if not article_text:
        article_text = """The government's new economic policy has sparked debate across the political spectrum. 
        Supporters argue it will create jobs and stimulate growth, while critics claim it will increase 
        the national debt and benefit only the wealthy. The bipartisan committee is reviewing the data 
        to determine the policy's effectiveness."""
        print("Using sample article...")
    
    print(f"\n📰 Analyzing article...")
    print(f"Text length: {len(article_text)} characters")
    
    # Analyze
    score, label, details = analyzer.classify_bias(article_text)
    
    print(f"\n🔍 Analysis Results:")
    print(f"Bias Label: {label}")
    print(f"Bias Score: {score:.3f}")
    print(f"Confidence: {details.get('confidence', 'unknown')}")
    
    print(f"\n📋 Detailed Breakdown:")
    print(f"  - Keyword Analysis: {details.get('keyword_label', 'N/A')} ({details.get('keyword_score', 0):.3f})")
    print(f"  - Sentiment Analysis: {details.get('sentiment_label', 'N/A')} ({details.get('sentiment_score', 0):.3f})")
    print(f"  - Loaded Language: {details.get('loaded_label', 'N/A')} ({details.get('loaded_score', 0):.3f})")
    
    if 'keyword_details' in details:
        print(f"\n🔤 Keyword Details:")
        for bias, score in details['keyword_details'].items():
            print(f"  - {bias.capitalize()}: {score:.3f}")

if __name__ == "__main__":
    # Run automated tests
    test_bias_detection()
    
    # Test custom article
    test_custom_article() 