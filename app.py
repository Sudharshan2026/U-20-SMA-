import streamlit as st
import pandas as pd
from langflow.load import run_flow_from_json
import plotly.express as px

# Set page configuration at the beginning
st.set_page_config(page_title="Social Media Insights", layout="wide")

# Sidebar for navigation and file upload
st.sidebar.title("Navigation")
option = st.sidebar.radio("Go to", ("Visualize","Insights", "Chat"))

uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv", "txt", "json"])

# Add a help section in the sidebar
st.sidebar.markdown("## Help")
st.sidebar.markdown("1. **Insights**: Upload a CSV file and click 'Generate Insights' to analyze post performance and generate recommendations.")
st.sidebar.markdown("2. **Chat**: Upload a file and enter your query to get social media data analysis.")
st.sidebar.markdown("3. **Visualize**: Upload a CSV file to visualize social media performance insights.")


if option == "Insights":
    # Insights Code
    # Define tweaks configuration for LangFlow
    TWEAKS = {
        "ChatInput-XWipW": {
            "input_value": "The input dataset contains the following columns:\n\nPlatform: The social media platform (e.g., Instagram, TikTok, LinkedIn, etc.).\nPostID: A unique identifier for each post.\nPostType: The type of post (e.g., reel, carousel, video, photo, story).\nPostTimestamp: The date when the post was published.\nLikes: Total likes the post received.\nComments: Total comments the post received.\nShares: Total shares the post received.\nImpressions: Total number of times the post was seen.\nReach: Total number of unique accounts that saw the post.\nUse this data to analyze post performance, generate insights, and provide recommendations."
        },
        "Prompt-5VzY2": {
            "template": "{context}\n\n---\nAnalyze the performance of the social media posts using the input dataset. Generate detailed and actionable insights by focusing on the following aspects:\n\nPost Type Analysis\n\nCompare the performance of different post types (e.g., reel, carousel, video, photo, story) based on metrics like engagement rate, impressions, and reach.\nIdentify the top-performing post type and explain why.\nPlatform Performance\n\nEvaluate which platform performs best for each post type.\nHighlight platform-specific strengths and weaknesses.\nEngagement Trends\n\nIdentify trends over time, such as periods of high engagement or declines.\nHighlight any standout days, weeks, or post types with unusually high or low performance.\nAudience Interaction\n\nAssess which metrics (likes, comments, shares) contribute most to engagement for specific post types or platforms.\nOptimization Recommendations\n\nProvide actionable recommendations based on the insights.\nSuggest posting strategies to maximize reach and engagement.\nQuestion: {question}\n{History}\nAnswer: "
        },
        "File-XCz1E": {
            "path": "social.csv"
        },
        "OllamaModel-Ksd7O": {
            "system_message": "You are a data analysis assistant specializing in social media performance optimization. Your task is to analyze the given dataset and produce insights that are data-driven, concise, and actionable. Focus on comparing post types and platforms. Use metrics like engagement rate, impressions, and reach for meaningful analysis. Provide practical recommendations for improving content strategy. Ensure outputs are easy to understand and directly applicable. Format the insights as clear, data-backed bullet points.",
            "temperature": 0.2
        }
    }

    # Streamlit App
    st.title("Social Media Insights Generator")
    st.markdown("Upload your dataset and click 'Generate Insights' to analyze post performance and generate recommendations.")

    if uploaded_file:
        try:
            # Read the uploaded CSV
            df = pd.read_csv(uploaded_file)
            st.sidebar.success("File uploaded successfully!")
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
        except Exception as e:
            st.sidebar.error(f"Error reading the file: {e}")

    # Button to generate insights
    if st.button("Generate Insights"):
        if not uploaded_file:
            st.error("Please upload a CSV file first.")
        else:
            try:
                # Save uploaded file temporarily for LangFlow input
                temp_path = "temp_social.csv"
                df.to_csv(temp_path, index=False)
                TWEAKS["File-XCz1E"]["path"] = temp_path

                # Run LangFlow flow
                with st.spinner("Generating insights..."):
                    result = run_flow_from_json(
                        flow="E:\\lang12\\socialpost\\annadone.json",
                        session_id="",
                        fallback_to_env_vars=True,
                        tweaks=TWEAKS,
                        input_value=TWEAKS["ChatInput-XWipW"]["input_value"]
                    )

                # Display results
                if isinstance(result, list) and len(result) > 0:
                    first_result = result[0]
                    try:
                        message = first_result.outputs[0].results['message'].data['text']
                        st.success("Insights Generated Successfully:")
                        st.markdown(message)
                    except AttributeError as e:
                        st.error(f"Error extracting data: {e}")
                else:
                    st.error("No results returned from LangFlow or unexpected format.")

            except Exception as e:
                st.error(f"Error during analysis: {e}")

elif option == "Visualize":
    # Visualize Code
    if uploaded_file:
        try:
            # Load dataset
            data = pd.read_csv(uploaded_file)

            # Convert PostTimestamp to datetime and extract time-based information
            data['PostTimestamp'] = pd.to_datetime(data['PostTimestamp'])
            data['Month'] = data['PostTimestamp'].dt.month_name()
            data['Week'] = data['PostTimestamp'].dt.isocalendar().week

            # Title and Introduction
            st.title("📊 Social Media Performance Insights")
            st.write("""
            Welcome to the interactive dashboard! Here, you can explore the performance of various platforms and post types,
            compare engagement metrics, and gain actionable insights from the data. Use the filters below to customize your view.
            """)

            # Filters for interactivity
            platforms = st.multiselect("Select Platform(s):", options=data["Platform"].unique(), default=data["Platform"].unique())
            post_types = st.multiselect("Select Post Type(s):", options=data["PostType"].unique(), default=data["PostType"].unique())

            # Filter data based on selection
            filtered_data = data[(data["Platform"].isin(platforms)) & (data["PostType"].isin(post_types))]

            # KPIs Section
            st.header("📈 Key Performance Indicators")
            total_likes = filtered_data["Likes"].sum()
            total_comments = filtered_data["Comments"].sum()
            total_shares = filtered_data["Shares"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("👍 Total Likes", f"{total_likes:,}")
            col2.metric("💬 Total Comments", f"{total_comments:,}")
            col3.metric("🔗 Total Shares", f"{total_shares:,}")

            # -----------------------------
            # Pie Chart: Platform Engagement Share
            # -----------------------------
            st.header("📊 Platform Engagement Share")
            platform_engagement = filtered_data.groupby('Platform')[['Likes', 'Comments', 'Shares']].sum().sum(axis=1).reset_index()
            platform_engagement.columns = ["Platform", "TotalEngagement"]

            pie_chart = px.pie(
                platform_engagement,
                names="Platform",
                values="TotalEngagement",
                title="Engagement Share by Platform",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(pie_chart, use_container_width=True)

            # -----------------------------
            # Line Chart: Monthly Trends for Engagement
            # -----------------------------
            st.header("📅 Monthly Engagement Trends")
            monthly_trends = filtered_data.groupby(['Month', 'Platform'])[['Likes', 'Comments', 'Shares']].sum().reset_index()
            monthly_trends["TotalEngagement"] = monthly_trends["Likes"] + monthly_trends["Comments"] + monthly_trends["Shares"]

            line_chart = px.line(
                monthly_trends,
                x="Month",
                y="TotalEngagement",
                color="Platform",
                title="Monthly Engagement Trends by Platform",
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(line_chart, use_container_width=True)

            # -----------------------------
            # Platform Performance (Bar Chart)
            # -----------------------------
            st.header("📌 Platform Performance")
            platform_performance = filtered_data.groupby('Platform')[['Likes', 'Comments', 'Shares']].sum().reset_index()
            platform_fig = px.bar(
                platform_performance.melt(id_vars="Platform", var_name="Metric", value_name="Count"),
                x="Platform",
                y="Count",
                color="Metric",
                title="Platform Performance by Engagement Metrics",
                barmode="group",
                text_auto=True,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(platform_fig, use_container_width=True)

            # -----------------------------
            # Post Type Performance (Bar Chart)
            # -----------------------------
            st.header("📝 Post Type Performance")
            post_type_performance = filtered_data.groupby('PostType')[['Likes', 'Comments', 'Shares']].mean().reset_index()
            post_type_fig = px.bar(
                post_type_performance.melt(id_vars="PostType", var_name="Metric", value_name="Average"),
                x="PostType",
                y="Average",
                color="Metric",
                title="Average Engagement by Post Type",
                barmode="group",
                text_auto=True,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(post_type_fig, use_container_width=True)

            # -----------------------------
            # Scatter Plot: Post Frequency vs Engagement
            # -----------------------------
            st.header("🔄 Post Frequency vs Engagement")
            post_frequency = filtered_data.groupby(['Platform', 'PostType']).size().reset_index(name='PostCount')
            engagement = filtered_data.groupby(['Platform', 'PostType'])[['Likes', 'Comments', 'Shares']].mean().reset_index()
            merged = pd.merge(post_frequency, engagement, on=['Platform', 'PostType'])
            merged['TotalEngagement'] = merged['Likes'] + merged['Comments'] + merged['Shares']

            scatter_fig = px.scatter(
                merged,
                x="PostCount",
                y="TotalEngagement",
                size="PostCount",
                color="Platform",
                hover_data=['PostType'],
                title="Post Frequency vs Total Engagement",
                color_discrete_sequence=px.colors.qualitative.Set1,
                size_max=60
            )
            st.plotly_chart(scatter_fig, use_container_width=True)

            # Closing note
            st.write("### 🔍 Explore the data further using the filters above and identify actionable insights!")

        except Exception as e:
            st.error(f"Error loading or processing the file: {e}")
    else:
        st.error("Please upload a file first.") 
      
elif option == "Chat":
    # Chat Code
    # Define tweaks and flow configuration
    TWEAKS = {
        "ChatInput-JQ9je": {
            "input_value": "",
            "sender": "User",
            "sender_name": "User",
            "should_store_message": True
        },
        "ParseData-u0VG7": {
            "sep": "\n",
            "template": "{text}"
        },
        "Prompt-kNXeh": {
            "template": "{context}\n\n---\n\nGiven the context above, answer the question as best as possible.\n\nQuestion: {question}\n\nAnswer: "
        },
        "ChatOutput-f7PPp": {
            "data_template": "{text}",
            "sender": "Machine",
            "sender_name": "AI",
            "should_store_message": True
        },
        "Chroma-Hf7kl": {
            "allow_duplicates": False,
            "collection_name": "social2",
            "persist_directory": "E:\\lang12\\chroma",
            "number_of_results": 10,
            "search_type": "Similarity"
        },
        "OllamaModel-82WGy": {
            "base_url": "http://localhost:11434",
            "model_name": "llama3:latest",
            "temperature": 0.2
        }
    }

    # Streamlit UI
    st.title("LangFlow Interface for Social Media Analysis")

    # Preview uploaded file
    if uploaded_file is not None:
        st.sidebar.write("### Preview of Uploaded File:")
        try:
            if uploaded_file.type == "text/csv":
                data = pd.read_csv(uploaded_file)
                st.sidebar.dataframe(data)
            elif uploaded_file.type == "application/json":
                import json
                data = json.load(uploaded_file)
                st.sidebar.json(data)
            else:
                content = uploaded_file.read().decode("utf-8")
                st.sidebar.text(content)
        except Exception as e:
            st.sidebar.error(f"Error previewing the file: {e}")

    # User inputs
    st.write("Enter your query for social media data analysis:")
    input_value = st.text_input("Query", value="What is the average likes in the LinkedIn?")

    run_analysis = st.button("Run Analysis")

    if run_analysis:
        with st.spinner("Processing..."):
            try:
                result = run_flow_from_json(
                    flow="E:\\lang12\\socialpost\\annac.json",
                    session_id="",
                    fallback_to_env_vars=True,
                    tweaks=TWEAKS,
                    input_value=input_value
                )

                if isinstance(result, list) and len(result) > 0:
                    first_result = result[0]
                    try:
                        message = first_result.outputs[0].results['message'].data['text']
                        st.success("### Generated Output:")
                        st.write(message)
                    except AttributeError as e:
                        st.error(f"Error extracting data: {e}")
                else:
                    st.error("No results returned from LangFlow or unexpected format.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

