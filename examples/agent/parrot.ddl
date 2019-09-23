metadata :name        => "parrot",
         :description => "Example python agent",
         :author      => "Ben Roberts <me@benroberts.net>",
         :license     => "Apache-2.0",
         :version     => "0.1",
         :url         => "https://github.com/optiz0r/py-mco-agent",
         :timeout     => 10


action "echo", :description => "Example task which returns the given message" do
  display :always

  input :message,
        :prompt      => "Message",
        :description => "Message to be repeated back",
        :type        => :string,
        :validation  => "^.*$",
        :maxlength   => 0,
        :optional    => false




  output :message,
         :description => "Message",
         :display_as  => "Message",
         :type        => ""

end

action "invalid", :description => "Example task which always fails" do
  display :failed



end

