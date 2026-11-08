ListView.builder(
  itemCount: channelList.length, // Saare channels ki ginti
  itemBuilder: (context, index) {
    return ListTile(
      leading: Image.network(channelList[index]['logo']), // Channel ka Logo
      title: Text(channelList[index]['name']), // Channel ka Naam
      subtitle: Text("Live"), 
      trailing: Icon(Icons.play_arrow), // Play button ka icon
      onTap: () {
        // Yahan par click karne par Video Player open hoga
        openVideoPlayer(channelList[index]['url']);
      },
    );
  },
);
