# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
from typing import Annotated
from collections.abc import Coroutine

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import (
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.core_plugins.time_plugin import TimePlugin
from semantic_kernel.data.kernel_search_results import KernelSearchResults
from semantic_kernel.data.vector_search.vector_search_result import VectorSearchResult
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.kernel import Kernel


from semantic_kernel.connectors.memory.azure_ai_search import AzureAISearchCollection, AzureAISearchStore
from semantic_kernel.data.vector_search import VectorSearchOptions
from semantic_kernel.connectors.ai.open_ai.services.azure_text_embedding import AzureTextEmbedding

from semantic_kernel.filters.filter_types import FilterTypes
from semantic_kernel.filters.functions.function_invocation_context import FunctionInvocationContext

from plugins.models.HotelDataModel import HotelSampleClass

# Create a Azure AI Search VectorStore object and choose an existing collection that already contains records.
# Hotels is the data model decorated class.
store = AzureAISearchStore()
collection: AzureAISearchCollection[str, HotelSampleClass] = store.get_collection(
    "hotels-sample-index1", HotelSampleClass)
vector_search_options = VectorSearchOptions(
    vector_field_name="description_vector", top=2)
embeddings = AzureTextEmbedding(
    service_id="embedding", deployment_name="text-embedding-3-small", env_file_path="embedding.env")
# Generate a vector for your search text.
# Just showing a placeholder method here for brevity.


# async def main():
#     search_vectors = await embeddings.generate_embeddings(texts=["I'm looking for a hotel where there is Free WiFi"])
#     search_result = await collection.vectorized_search(vector=search_vectors[0], options=vector_search_options)
#     products = [record async for record in search_result.results]

#     output = await collection.text_search("Free WiFi")
#     # collection.vectorizable_text_search()
#     hotels = [record.record async for record in output.results]
#     print(f"Found hotels: {hotels}")
#     # search_results = await collection.vectorized_search(
#     #     vector=vector, options=VectorSearchOptions(vector_field_name="vector")
#     # )
#     # hotels = [record.record async for record in search_results.results]
#     # print(f"Found hotels: {hotels}")


# if __name__ == "__main__":
#     asyncio.run(main())
from typing import TypedDict, Annotated

class HotelBasics(TypedDict):
   hotel_id: str
   description: str
   rating: float

class HotelSearch:
    """A plugin that provides hotel information."""

    @kernel_function(name="search", description="Search for hotels using the query of the user")
    async def get_matching_hotels(self, query: Annotated[str, "The input query to semantically search for the best hotels"]) -> Annotated[str, "The list of matched hotels"]:
        search_vectors = await embeddings.generate_embeddings(texts=[query])
        search_result: KernelSearchResults[VectorSearchResult[HotelSampleClass]] = await collection.vectorized_search(vector=search_vectors[0], options=vector_search_options)
        # products = [record async for record in search_result.results]

        # output = await collection.text_search("Free WiFi")
        # collection.vectorizable_text_search()
        
        hotels: list[HotelBasics] = [ HotelBasics(description=record.record.description,hotel_id=record.record.hotel_id,rating=record.record.rating) async for record in search_result.results]
        print(f"Found hotels: {hotels}")
        return json.dumps(hotels)
    
    @kernel_function(name="get_hotel", description="Search for hotels using the hotel_id")
    async def get_hotel(self, hotel_id: Annotated[str, "The id of the hotel "]) -> Annotated[str, "The details of the hotel"]:
        
        hotel = await collection.get(key=hotel_id)
        if hotel:
            return hotel.model_dump_json()
        return ""
    
    @kernel_function(name="book_hotel", description="Books the hotel using the hotel_id")
    async def book_hotel(self, hotel_id: Annotated[str, "The id of the hotel "]) -> Annotated[str, "The details of the booking"]:
        print(f"Booked hotel_id: {hotel_id}")
        return "The hotel is booked."
    
    # This filter will log all calls to the Azure AI Search plugin.
    # This allows us to see what parameters are being passed to the plugin.
    # And this gives us a way to debug the search experience and if necessary tweak the parameters and descriptions.
    # @kernel.filter(filter_type=FilterTypes.FUNCTION_INVOCATION)
    # async def log_search_filter(self, context: FunctionInvocationContext, next: Coroutine[FunctionInvocationContext, any, None]):
    #     if context.function.plugin_name == "azure_ai_search":
    #         print(f"Calling Azure AI Search ({context.function.name}) with arguments:")
    #         for arg in context.arguments:
    #             if arg in ("user_input", "chat_history"):
    #                 continue
    #             print(f'  {arg}: "{context.arguments[arg]}"')
    #         await next(context)
    #     else:
    #         await next(context)
