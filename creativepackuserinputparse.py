"""
based on user input, expand prompts for ....
then construct statistics - write point form for statistics and find relevant graphs

"""
from elements_gen_process import get_prompts_1, get_prompts_2, expand_flux_prompts, multiple_image_prediction
import asyncio 
from utils.initialize_client import create_openai_completion

async def refine_and_generate_main(target_audience, stylistic_description, content_description):
    prompt_list_1 = get_prompts_1()
    descriptions = await expand_flux_prompts(target_audience, stylistic_description, content_description, prompt_list_1)
    await multiple_image_prediction(descriptions)

async def refine_and_generate_points(target_audience, stylistic_description, content_description, statistics):
    prompt_list_2 = get_prompts_2()
    for statistic in statistics:
        prompt = "This is a general content theme" + content_description + f"; rewrite the content description to better fit this statistic : {statistic}"
        create_openai_completion(prompt)
        content_description_temp = content_description + f"; rewrite the content description to better fit this statistic; {statistic}"
        descriptions = await expand_flux_prompts(target_audience, stylistic_description, content_description_temp, prompt_list_2)
        await multiple_image_prediction(descriptions)

def find_graphs():
    pass


# async def main():
#     target_audience = "early teens still in school"
#     stylistic_description = "cartoonish, colorful and engaging"
#     content_description = "the harmful effects of cannabis on growing up"
#     statistics = ["38% of teens have felt peer pressure to try weed", "97% of teens have heard about weed", "100% of cheese is drippy"]

#     for i in range(3):
#         await refine_and_generate_main(target_audience, stylistic_description, content_description)
#     await refine_and_generate_points(target_audience, stylistic_description, content_description, statistics)

# if __name__ == "__main__":
#     asyncio.run(main())